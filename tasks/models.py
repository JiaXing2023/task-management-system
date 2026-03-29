from django.db import models
from django.conf import settings  # 使用 settings.AUTH_USER_MODEL 引用自定义用户模型
from django.utils import timezone


class Task(models.Model):
    """
    任务模型，完全匹配前端需求
    """
    STATUS_CHOICES = (
        ('pending', '待完成'),
        ('completed', '已完成'),
        ('overdue', '已逾期'),
    )

    title = models.CharField(max_length=200, verbose_name="任务名称")
    manager = models.CharField(max_length=50, verbose_name="负责人")
    create_time = models.DateField(verbose_name="创建时间")
    deadline = models.DateField(verbose_name="截止时间")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="任务状态"
    )
    desc = models.TextField(blank=True, verbose_name="任务描述")

    # 可选：关联用户（如果任务需要归属某个用户）
    # user = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     verbose_name="所属用户"
    # )

    class Meta:
        db_table = 'tasks'
        verbose_name = "任务"
        verbose_name_plural = "任务"
        ordering = ['-create_time']

    def __str__(self):
        return self.title


class LoginRecord(models.Model):
    """
    用户登录记录模型
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="用户"
    )
    username = models.CharField(max_length=150, verbose_name="登录用户名")
    ip_address = models.CharField(max_length=50, verbose_name="IP地址")
    login_time = models.DateTimeField(default=timezone.now, verbose_name="登录时间")
    is_success = models.BooleanField(default=False, verbose_name="是否登录成功")
    error_msg = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="错误信息"
    )

    class Meta:
        verbose_name = "登录记录"
        verbose_name_plural = "登录记录"
        ordering = ['-login_time']

    def __str__(self):
        return f"{self.username} - {'成功' if self.is_success else '失败'} - {self.login_time.strftime('%Y-%m-%d %H:%M:%S')}"