# users/urls.py
"""
用户模块URL配置
负责用户注册、登录、个人信息等接口的路由映射
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response

# 导入视图类
from .views import (
    RegisterView,
    send_sms_code,  # 发送验证码视图
    verify_code,  # 验证验证码视图
    phone_login  # 手机号登录视图（可选）
)


# 定义健康检查接口（可选，方便前端/运维排查问题）
@api_view(['GET'])
def health_check(request):
    """用户模块健康检查接口"""
    return Response({
        "status": "success",
        "module": "users",
        "message": "用户模块接口正常"
    })


# 路由配置
urlpatterns = [
    # 健康检查接口：GET /api/register/health/
    path('health/', health_check, name='user_health_check'),

    # 用户注册接口：POST /api/register/
    # 空路径匹配根路由 /api/register/，适配你之前的配置
    path('', RegisterView.as_view(), name='user_register'),

    # ========== 验证码相关接口 ==========
    # 发送验证码：POST /api/register/send-code/
    path('send-code/', send_sms_code, name='send_code'),

    # 验证验证码：POST /api/register/verify-code/
    path('verify-code/', verify_code, name='verify_code'),

    # 手机号登录：POST /api/register/phone-login/
    path('phone-login/', phone_login, name='phone_login'),
]

# 全局路由命名空间（可选，避免路由名称冲突）
app_name = 'users'