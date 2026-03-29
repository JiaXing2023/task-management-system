from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Role  # 必需导入，已添加

# 获取当前激活的用户模型（即 users.User）
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器，包含注册和用户信息展示
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        label="密码"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        label="确认密码"
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'password',
            'password2',
            'email',
            'phone',
            'avatar',
            'gender',
            'id_card',
            'role',
            'status',
            'permissions'
        )
        extra_kwargs = {
            'username': {'label': '用户名'},
            'email': {'label': '电子邮箱'},
            'phone': {'label': '手机号'},
            'avatar': {'label': '头像URL'},
            'gender': {'label': '性别'},
            'id_card': {'label': '身份证号'},
            'role': {'label': '角色'},
            'status': {'label': '状态'},
            'permissions': {'label': '权限'}
        }

    def validate(self, attrs):
        """验证两次密码是否一致"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "两次密码不一致"})
        return attrs

    def create(self, validated_data):
        """创建用户"""
        # 移除确认密码字段
        validated_data.pop('password2')

        # 创建用户（使用 create_user 会自动加密密码）
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        # 设置其他扩展字段
        if 'phone' in validated_data:
            user.phone = validated_data['phone']
        if 'avatar' in validated_data:
            user.avatar = validated_data['avatar']
        if 'gender' in validated_data:
            user.gender = validated_data['gender']
        if 'id_card' in validated_data:
            user.id_card = validated_data['id_card']
        if 'role' in validated_data:
            user.role = validated_data['role']
        if 'status' in validated_data:
            user.status = validated_data['status']
        if 'permissions' in validated_data:
            user.permissions = validated_data['permissions']

        user.save()
        return user

    def update(self, instance, validated_data):
        """更新用户信息（用于个人中心修改）"""
        # 处理密码更新
        if 'password' in validated_data:
            validated_data.pop('password2', None)  # 移除确认密码
            instance.set_password(validated_data.pop('password'))

        # 更新其他字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


# 可选：简化版的用户信息序列化器（用于展示，不包含敏感信息）
class UserProfileSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'avatar', 'gender', 'role', 'status', 'permissions')


# 你要求添加的角色序列化器
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'