# employee_system/tasks/admin.py
from django.contrib import admin
from .models import Task, LoginRecord


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """任务模型的管理界面配置（匹配新模型字段）"""

    # 列表显示字段
    list_display = (
        'id',
        'title',
        'manager',
        'status',
        'create_time',
        'deadline',
    )

    # 列表可筛选字段
    list_filter = (
        'status',
        'create_time',
        'deadline',
    )

    # 搜索字段
    search_fields = (
        'title',
        'manager',
        'desc',
    )

    # 只读字段（详情页不可编辑）
    readonly_fields = (
        'id',
        'create_time',
    )

    # 列表页每页显示数量
    list_per_page = 20

    # 日期层级导航
    date_hierarchy = 'create_time'

    # 默认排序
    ordering = ['-create_time']

    # 字段分组（详情页布局）
    fieldsets = (
        ('基础信息', {
            'fields': ('title', 'manager', 'status', 'desc')
        }),
        ('时间信息', {
            'fields': ('create_time', 'deadline')
        }),
    )


@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    """登录记录管理界面配置"""

    list_display = (
        'id',
        'username',
        'ip_address',
        'login_time',
        'is_success',
    )

    list_filter = (
        'is_success',
        'login_time',
    )

    search_fields = (
        'username',
        'ip_address',
        'error_msg',
    )

    # 所有字段都只读，防止手动修改记录
    readonly_fields = (
        'user',
        'username',
        'ip_address',
        'login_time',
        'is_success',
        'error_msg',
    )

    ordering = ['-login_time']

    def has_add_permission(self, request):
        """禁止手动添加登录记录"""
        return False

    def has_change_permission(self, request, obj=None):
        """禁止修改登录记录"""
        return False

    def has_delete_permission(self, request, obj=None):
        """允许删除（可选，根据需求决定）"""
        return True  # 可以保留删除权限，用于清理日志