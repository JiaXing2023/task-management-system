# tasks/serializers.py
from rest_framework import serializers
from .models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    任务序列化器，完全匹配新模型字段
    """

    class Meta:
        model = Task
        fields = '__all__'  # 包含所有字段：id, title, manager, create_time, deadline, status, desc
        read_only_fields = ('id',)  # id 只读

    def to_representation(self, instance):
        """
        自定义返回格式，确保前端能正确接收
        """
        rep = super().to_representation(instance)
        # 保持字段名与前端一致
        return {
            'id': rep['id'],
            'title': rep['title'],
            'manager': rep['manager'],
            'createTime': rep['create_time'],  # 转换为驼峰命名，匹配前端
            'deadline': rep['deadline'],
            'status': rep['status'],
            'desc': rep.get('desc', '')  # 任务描述
        }

    def to_internal_value(self, data):
        """
        自定义接收格式，将前端的驼峰命名转换为模型字段
        """
        # 如果前端发送 createTime，转换为 create_time
        if 'createTime' in data:
            data['create_time'] = data.pop('createTime')

        return super().to_internal_value(data)