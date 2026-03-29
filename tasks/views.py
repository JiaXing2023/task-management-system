# tasks/views.py
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import render
from .models import Task
from .serializers import TaskSerializer
from users.throttling import UserApiThrottle, AnonApiThrottle


# 前端页面渲染视图
def index(request):
    """渲染前端任务管理页面"""
    return render(request, 'index.html')


# 方式1：使用 generics（更灵活，适合自定义响应格式）
class TaskListCreateView(generics.ListCreateAPIView):
    """任务列表和创建接口"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserApiThrottle, AnonApiThrottle]

    def get_queryset(self):
        """返回所有任务（因为没有 user 外键，所以返回全部）"""
        return Task.objects.all()

    def perform_create(self, serializer):
        """创建任务（无需关联用户）"""
        serializer.save()

    def list(self, request, *args, **kwargs):
        """自定义列表返回格式"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "code": 200,
            "data": serializer.data,
            "message": "获取任务列表成功"
        })

    def create(self, request, *args, **kwargs):
        """自定义创建返回格式"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 201,
            "message": "任务创建成功",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """任务详情、修改、删除接口"""
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserApiThrottle, AnonApiThrottle]

    def get_queryset(self):
        return Task.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """获取任务详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 200,
            "data": serializer.data,
            "message": "获取任务详情成功"
        })

    def update(self, request, *args, **kwargs):
        """更新任务"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 200,
            "message": "任务修改成功",
            "data": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        """删除任务"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 200,
            "message": "任务删除成功"
        }, status=status.HTTP_200_OK)


# 方式2：使用 ViewSet（更简洁，适合 RESTful 风格）
class TaskViewSet(viewsets.ModelViewSet):
    """
    任务视图集，提供完整的 CRUD 操作
    自动生成路由：/tasks/ (GET, POST), /tasks/{id}/ (GET, PUT, PATCH, DELETE)
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserApiThrottle, AnonApiThrottle]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """统计任务状态"""
        tasks = self.get_queryset()
        stats = {
            'total': tasks.count(),
            'pending': tasks.filter(status='pending').count(),
            'completed': tasks.filter(status='completed').count(),
            'overdue': tasks.filter(status='overdue').count()
        }
        return Response({
            "code": 200,
            "data": stats,
            "message": "获取统计数据成功"
        })

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """根据状态筛选任务"""
        status_param = request.query_params.get('status')
        if status_param:
            tasks = self.get_queryset().filter(status=status_param)
        else:
            tasks = self.get_queryset()
        serializer = self.get_serializer(tasks, many=True)
        return Response({
            "code": 200,
            "data": serializer.data,
            "message": f"获取{status_param}任务成功"
        })