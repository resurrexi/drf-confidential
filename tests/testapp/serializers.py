from rest_framework import serializers

from drf_confidential.mixins import PrivateFieldsMixin

from .models import Employee, Profile, EmployeeJob, Post


class EmployeeSerializer(PrivateFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        private_fields = (
            "address_1",
            "address_2",
            "country",
            "city",
            "phone_number",
        )
        user_relation = "login_account"


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"


class EmployeeJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeJob
        fields = "__all__"
        private_fields = ("salary",)
        private_permission = "view_employee_salary"


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        private_fields = ("secret_note",)
