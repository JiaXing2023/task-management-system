"""
任务模块URL配置
适配TaskListCreateView/TaskDetailView，支持完整CRUD接口
解决404问题，支持前后端开发
"""
from django.urls import path
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .views import TaskListCreateView, TaskDetailView  # 保留原有视图导入

# 任务模块根路径接口（访问 /api/tasks/ 时显示，解决404）
@api_view(['GET'])
def task_root(request):
    """任务模块根接口（展示所有可用接口）"""
    return Response({
        "code": 200,
        "message": "任务模块根接口",
        "available_endpoints": [
            "/api/tasks/health/",          # 健康检查
            "/api/tasks/tasks/",           # 任务列表/创建（GET/POST）
            "/api/tasks/tasks/<int:pk>/",  # 任务详情/修改/删除（GET/PUT/DELETE）
        ]
    })

# 任务模块健康检查接口
@api_view(['GET'])
def task_health_check(request):
    """任务模块健康检查接口"""
    return Response({
        "status": "success",
        "module": "tasks",
        "message": "任务模块接口正常运行",
        "available_endpoints": [
            "/api/tasks/health/",
            "/api/tasks/tasks/",
            "/api/tasks/tasks/<int:pk>/",
        ]
    })

# 核心路由配置
urlpatterns = [
    # 根路径：访问 /api/tasks/ 时返回接口说明（保留，解决404）
    path('', task_root, name='task_root'),
    # 健康检查接口（保留）
    path('health/', task_health_check, name='task_health_check'),
    # 任务列表/创建接口：GET（查列表）、POST（创建）（保留原有路径，核心API）
    path('tasks/', TaskListCreateView.as_view(), name='task_list_create'),
    # 任务详情/修改/删除接口：GET（查单条）、PUT（修改）、DELETE（删除）（保留）
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
]

app_name = 'tasks'