# admin_context.py
from django.contrib.auth.models import User
from django.utils import timezone
from tasks.models import Task


def admin_dashboard_context(request):
    """给 Admin 首页注入统计数据，仅作用于Admin模板，不影响前后端接口"""
    # 获取今日日期（Django时区标准写法，避免时间偏移）
    today = timezone.now().date()

    # 统计数据（字段名完全匹配Task模型的completed字段）
    return {
        # 用户维度统计
        "total_users": User.objects.count(),  # 总用户数
        "today_new_users": User.objects.filter(date_joined__date=today).count(),  # 今日新增用户

        # 任务维度统计（核心：用completed字段，和数据库一致）
        "total_tasks": Task.objects.count(),  # 总任务数
        "pending_tasks": Task.objects.filter(completed=False).count(), # 待办任务数（未完成）
        "completed_tasks": Task.objects.filter(completed=True).count(),  # 新增：已完成任务数（可选）
    }