from rest_framework.viewsets import ModelViewSet

from drf_confidential.permissions import ConfidentialFieldsPermission

from .serializers import (
    EmployeeSerializer,
    ProfileSerializer,
    EmployeeJobSerializer,
    PostSerializer,
)
from .models import Employee, Profile, EmployeeJob, Post


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = (ConfidentialFieldsPermission,)


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class EmployeeJobViewSet(ModelViewSet):
    serializer_class = EmployeeJobSerializer
    queryset = EmployeeJob.objects.all()
    permission_classes = (ConfidentialFieldsPermission,)


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = (ConfidentialFieldsPermission,)
