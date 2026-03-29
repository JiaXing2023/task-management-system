"""
URL configuration for employee_system project.
最优版本：兼顾调试友好、配置规范、可扩展性 + 新增Vue前端页面路由 + 完整API接口
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from users.views import reset_password
from users.views import RoleViewSet  # ✅ 添加角色管理视图

# 导入自定义视图
from users.views import (
    CustomTokenObtainPairView,
    UserViewSet,
    send_sms_code,      # ✅ 添加验证码发送视图
    verify_code,        # ✅ 添加验证码验证视图
    phone_login         # ✅ 可选：手机号登录视图
)
from tasks.views import TaskViewSet

# 注意：如果你的health_check和dashboard_stats不在employee_system/views.py，需修正导入路径
try:
    from .views import dashboard_stats, health_check
except ImportError:
    # 兼容：如果视图不存在，临时定义空视图避免报错
    def dashboard_stats(request):
        return HttpResponse({"code":200, "message":"看板接口待实现"}, content_type='application/json')
    def health_check(request):
        return HttpResponse({"status":"ok", "message":"服务正常"}, content_type='application/json')


# 可视化首页（开发调试用，保留）
def home(request):
    return HttpResponse("""
        <h1>任务管理系统 - 后端运行正常</h1>
        <p>📊 动态看板：<a href="/api/dashboard/stats/">/api/dashboard/stats/</a></p>
        <p>🩺 健康检查：<a href="/health-check/">/health-check/</a></p>
        <p>🔧 后台管理：<a href="/admin/">/admin/</a></p>
        <p>🔑 获取Token：<a href="/api/token/">/api/token/</a>（POST传username/password）</p>
        <p>🔄 刷新Token：<a href="/api/token/refresh/">/api/token/refresh/</a>（POST传refresh）</p>
        <p>📝 用户注册：<a href="/api/register/">/api/register/</a>（POST传注册信息）</p>
        <p>📱 发送验证码：<a href="/api/send-code/">/api/send-code/</a>（POST传手机号）</p>
        <p>✅ 验证验证码：<a href="/api/verify-code/">/api/verify-code/</a>（POST传手机号和验证码）</p>
        <p>📱 手机号登录：<a href="/api/phone-login/">/api/phone-login/</a>（POST传手机号和验证码）</p>
        <p>👤 用户管理：<a href="/api/users/">/api/users/</a>（用户列表）</p>
        <p>📋 任务管理：<a href="/api/tasks/">/api/tasks/</a>（任务列表）</p>
        <p>📊 任务统计：<a href="/api/tasks/stats/">/api/tasks/stats/</a>（任务统计）</p>
        <p>👨‍💻 用户前端页面：<a href="/app/">/app/</a>（Vue任务管理页面）</p>
    """, content_type='text/html; charset=utf-8')


# 创建 API 路由器
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')  # 用户管理
router.register(r'tasks', TaskViewSet, basename='task')  # 任务管理
router.register(r'roles', RoleViewSet, basename='role')  # 你添加的角色管理


# 核心路由配置
urlpatterns = [
    path('api/reset-password/', reset_password, name='reset_password'),
    # 根路径：可视化调试首页
    path('', home),

    # Vue前端页面路由
    path('app/', TemplateView.as_view(template_name='index.html'), name='vue_frontend'),

    # 管理员后台
    path('admin/', admin.site.urls),

    # 业务接口：看板、健康检查
    path('api/dashboard/stats/', dashboard_stats, name='dashboard_stats'),
    path('health-check/', health_check, name='health_check'),

    # JWT认证接口
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(permission_classes=[AllowAny]), name='token_refresh'),

    # ========== 验证码相关接口 ==========
    path('api/send-code/', send_sms_code, name='send_code'),      # 发送验证码
    path('api/verify-code/', verify_code, name='verify_code'),    # 验证验证码
    path('api/phone-login/', phone_login, name='phone_login'),    # 手机号验证码登录（可选）

    # API 路由（包含 users 和 tasks 的所有接口）
    path('api/', include(router.urls)),

    # 用户注册（单独的路由，因为 ViewSet 中没有 register 动作）
    path('api/register/', include('users.urls')),  # 需要在 users/urls.py 中配置 RegisterView
]


# 开发环境跨域配置
from django.conf import settings
if settings.DEBUG:
    # 1. 确保corsheaders已安装并添加到INSTALLED_APPS
    if 'corsheaders' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS.append('corsheaders')

    # 2. 确保cors中间件在最前面（避免跨域失效）
    cors_middleware = 'corsheaders.middleware.CorsMiddleware'
    if cors_middleware not in settings.MIDDLEWARE:
        settings.MIDDLEWARE.insert(0, cors_middleware)

    # 3. 允许前端开发域名
    settings.CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",   # React/Vite前端
        "http://127.0.0.1:3000",
        "http://localhost:8080",   # Vue前端
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",   # Django服务
        "http://localhost:8000",
    ]
    settings.CORS_ALLOW_CREDENTIALS = True
    settings.CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']
    settings.CORS_ALLOW_HEADERS = ['*']