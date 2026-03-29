# users/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model, authenticate
from django.db import IntegrityError
from django.utils import timezone

# DRF相关导入
from rest_framework import generics, permissions, status, viewsets, serializers  # ✅ 添加 serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

# JWT相关导入
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# 导入自定义序列化器
from .serializers import UserSerializer

# 导入验证码模型
from .models import VerificationCode

import random
import re
# 你要求添加的代码（原样添加，无任何修改）
from .models import Role
from .serializers import RoleSerializer

User = get_user_model()  # 获取当前激活的用户模型（即 users.User）


# ------------------- JWT登录接口（已修改：添加角色验证） -------------------
# 自定义JWT序列化器：返回更多用户信息
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['user_id'] = user.id
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # ✅ 检查用户状态（防止注销/禁用账号登录）
        if self.user.status != 'active':
            raise serializers.ValidationError('该账号已被禁用或注销，无法登录')

        data['username'] = self.user.username
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['role'] = self.user.role
        data['phone'] = self.user.phone
        data['avatar'] = self.user.avatar
        data['permissions'] = self.user.permissions
        return data


# 自定义JWT视图：指定序列化器 + 允许匿名访问
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


# ------------------- 用户注册接口（已修改：自动补全password2） -------------------
class RegisterView(generics.CreateAPIView):
    """
    用户注册接口
    接收POST请求，创建新用户，返回标准化响应
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        # ✅ 关键：如果前端没传 password2，自动用 password 填充
        data = request.data.copy()
        if 'password' in data and 'password2' not in data:
            data['password2'] = data['password']

        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response({
                "code": 200,
                "message": "用户注册成功",
                "data": {
                    "username": serializer.instance.username,
                    "email": serializer.instance.email,
                    "id": serializer.instance.id,
                    "role": serializer.instance.role
                }
            }, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({
                "code": 400,
                "message": "注册失败",
                "errors": {"username": "该用户名已存在"}
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": 400,
                "message": "注册失败",
                "errors": serializer.errors if hasattr(serializer, 'errors') else str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ------------------- 用户管理视图集（已修改：优化更新逻辑） -------------------
class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集，提供完整的CRUD操作
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前登录用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """更新当前用户信息"""
        user = request.user
        data = request.data.copy()

        # ✅ 检查用户状态（防止注销/禁用账号修改信息）
        if user.status != 'active':
            return Response({
                "code": 400,
                "message": "账号已被禁用或注销，无法修改"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ 处理密码更新（验证原密码）
        if 'newPassword' in data:
            if data.get('oldPassword') and user.check_password(data.get('oldPassword')):
                data['password'] = data.pop('newPassword')
                data.pop('confirmPassword', None)
            else:
                return Response({
                    "code": 400,
                    "message": "原密码错误"
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data=data, partial=True)
        if serializer.is_valid():
            # 如果密码在数据中，需要单独处理加密
            if 'password' in serializer.validated_data:
                user.set_password(serializer.validated_data.pop('password'))
            serializer.save()
            return Response({
                "code": 200,
                "message": "个人信息更新成功",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response({
            "code": 400,
            "message": "更新失败",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """退出登录（可选，用于黑名单token）"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()  # 需要启用黑名单
            return Response({"message": "退出成功"})
        except Exception:
            return Response({"message": "退出成功"})


# ------------------- 手机验证码功能 -------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def send_sms_code(request):
    """
    发送短信验证码
    请求格式: POST /api/send-code/
    {
        "phone": "13800138000",
        "type": "register"  # register, login, forgot
    }
    """
    phone = request.data.get('phone')
    code_type = request.data.get('type', 'register')

    if not phone:
        return Response({'error': '手机号不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查手机号格式
    if not re.match(r'^1[3-9]\d{9}$', phone):
        return Response({'error': '手机号格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

    # 根据类型进行额外验证
    if code_type == 'register':
        # 注册时检查手机号是否已注册
        if User.objects.filter(phone=phone, status='active').exists():
            return Response({'error': '该手机号已注册，请直接登录'}, status=status.HTTP_400_BAD_REQUEST)

    elif code_type == 'login':
        # 登录时检查手机号是否已注册
        if not User.objects.filter(phone=phone, status='active').exists():
            return Response({'error': '该手机号未注册，请先注册'}, status=status.HTTP_400_BAD_REQUEST)

    elif code_type == 'forgot':
        # 找回密码时检查手机号是否已注册
        if not User.objects.filter(phone=phone, status='active').exists():
            return Response({'error': '该手机号未注册或已被注销'}, status=status.HTTP_400_BAD_REQUEST)

    # 检查60秒内是否已发送过验证码
    last_code = VerificationCode.objects.filter(
        phone=phone,
        created_at__gte=timezone.now() - timezone.timedelta(seconds=60)
    ).first()

    if last_code:
        return Response({
            'error': '验证码发送过于频繁，请稍后再试'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # 生成6位随机验证码
    code = ''.join([str(random.randint(0, 9)) for _ in range(6)])

    # 保存验证码
    VerificationCode.objects.create(
        phone=phone,
        code=code
    )

    # 开发环境：打印验证码到控制台
    print(f"[验证码] {phone} - {code_type}: {code}")

    # 生产环境应该调用短信服务，开发环境返回验证码方便测试
    return Response({
        'message': '验证码已发送',
        'code': code,  # 开发环境返回，生产环境请删除
        'expires_in': 300
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_code(request):
    """
    验证验证码
    请求格式: POST /api/verify-code/
    {
        "phone": "13800138000",
        "code": "123456"
    }
    """
    phone = request.data.get('phone')
    code = request.data.get('code')

    if not phone or not code:
        return Response({'error': '手机号和验证码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    # 查找未使用的验证码（5分钟内有效）
    verification = VerificationCode.objects.filter(
        phone=phone,
        code=code,
        is_used=False,
        created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
    ).first()

    if not verification:
        return Response({'error': '验证码错误或已过期'}, status=status.HTTP_400_BAD_REQUEST)

    # 标记验证码为已使用
    verification.is_used = True
    verification.save()

    return Response({'message': '验证码验证成功'}, status=status.HTTP_200_OK)


# ------------------- 手机号验证码登录接口 -------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def phone_login(request):
    """
    手机号验证码登录
    请求格式: POST /api/phone-login/
    {
        "phone": "13800138000",
        "code": "123456"
    }
    """
    phone = request.data.get('phone')
    code = request.data.get('code')

    if not phone or not code:
        return Response({'error': '手机号和验证码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    # 验证验证码
    verification = VerificationCode.objects.filter(
        phone=phone,
        code=code,
        is_used=False,
        created_at__gte=timezone.now() - timezone.timedelta(minutes=5)
    ).first()

    if not verification:
        return Response({'error': '验证码错误或已过期'}, status=status.HTTP_400_BAD_REQUEST)

    # 查找用户
    try:
        user = User.objects.get(phone=phone, status='active')
    except User.DoesNotExist:
        return Response({'error': '用户不存在或已被禁用'}, status=status.HTTP_400_BAD_REQUEST)

    # 标记验证码为已使用
    verification.is_used = True
    verification.save()

    # 生成JWT token
    refresh = RefreshToken.for_user(user)

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'username': user.username,
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'phone': user.phone,
        'avatar': user.avatar,
        'permissions': user.permissions
    }, status=status.HTTP_200_OK)


# ------------------- 重置密码接口 -------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """
    重置密码接口
    请求格式: POST /api/reset-password/
    {
        "phone": "17711662767",
        "password": "newpassword123"
    }
    """
    phone = request.data.get('phone')
    new_password = request.data.get('password')

    if not phone or not new_password:
        return Response({'error': '手机号和新密码不能为空'}, status=status.HTTP_400_BAD_REQUEST)

    # 查找用户
    try:
        user = User.objects.get(phone=phone, status='active')
    except User.DoesNotExist:
        return Response({'error': '用户不存在或已被注销'}, status=status.HTTP_400_BAD_REQUEST)

    # 更新密码
    user.set_password(new_password)
    user.save()

    return Response({'message': '密码重置成功'}, status=status.HTTP_200_OK)


# 你要求添加的代码（原样添加，无任何修改）

class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图集"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # 只有管理员可以管理角色
        if self.request.user.role != 'admin':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()