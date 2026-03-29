# employee_system/views.py
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.utils import timezone
from tasks.models import Task
from django.db import connection

# ✅ 使用 get_user_model 获取当前激活的用户模型
User = get_user_model()


def dashboard_stats(request):
    """
    动态看板统计接口
    用于 Jazzmin 后台的仪表盘显示
    """
    try:
        today = timezone.now().date()

        # 用户统计
        total_users = User.objects.count()
        today_new_users = User.objects.filter(date_joined__date=today).count()

        # 任务统计（使用新字段 status 而不是 completed）
        total_tasks = Task.objects.count()
        pending_tasks = Task.objects.filter(status='pending').count()
        completed_tasks = Task.objects.filter(status='completed').count()
        overdue_tasks = Task.objects.filter(status='overdue').count()

        return JsonResponse({
            "total_users": total_users,
            "today_new_users": today_new_users,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks
        })
    except Exception as e:
        # 如果出错，返回默认值，避免前端显示错误
        return JsonResponse({
            "total_users": 0,
            "today_new_users": 0,
            "total_tasks": 0,
            "pending_tasks": 0,
            "completed_tasks": 0,
            "overdue_tasks": 0,
            "error": str(e)
        }, status=500)


def health_check(request):
    """
    健康检查接口
    检测数据库连接状态
    """
    # 检测数据库连接
    try:
        connection.ensure_connection()
        db_status = "connected"
        db_message = "数据库连接正常"
    except Exception as e:
        db_status = "error"
        db_message = f"数据库连接失败: {str(e)}"

    timestamp = timezone.now().isoformat()

    return JsonResponse({
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "timestamp": timestamp,
        "database": {
            "status": db_status,
            "message": db_message
        },
        "django_version": "4.2.29",
        "python_version": "3.9",
        "user_model": str(User.__name__)
    })