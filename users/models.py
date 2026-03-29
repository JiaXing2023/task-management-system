from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    自定义用户模型，扩展默认 User，增加前端所需字段
    """
    phone = models.CharField(max_length=20, blank=True, verbose_name="手机号")
    avatar = models.URLField(blank=True, verbose_name="头像URL")
    gender = models.CharField(
        max_length=2,
        choices=[('男', '男'), ('女', '女')],
        blank=True,
        verbose_name="性别"
    )
    id_card = models.CharField(max_length=18, blank=True, verbose_name="身份证号")
    role = models.CharField(
        max_length=10,
        choices=[('admin', '管理员'), ('user', '普通员工')],
        default='user',
        verbose_name="角色"
    )
    status = models.CharField(
        max_length=10,
        choices=[
            ('active', '启用'),
            ('inactive', '禁用'),
            ('cancelled', '已注销')
        ],
        default='active',
        verbose_name="状态"
    )
    permissions = models.JSONField(default=dict, verbose_name="权限")

    class Meta:
        db_table = 'users'
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    """
    短信/邮箱验证码模型
    """
    phone = models.CharField(max_length=20, db_index=True, verbose_name="手机号")
    code = models.CharField(max_length=6, verbose_name="验证码")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    is_used = models.BooleanField(default=False, verbose_name="是否已使用")

    class Meta:
        db_table = 'verification_codes'
        verbose_name = "验证码"
        verbose_name_plural = "验证码"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone} - {self.code}"


class Role(models.Model):
    """角色模型"""
    name = models.CharField(max_length=50, verbose_name="角色名称")
    description = models.TextField(blank=True, verbose_name="角色描述")
    permissions = models.JSONField(default=dict, verbose_name="权限")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = 'roles'
        verbose_name = "角色"
        verbose_name_plural = "角色"

    def __str__(self):
        return self.name