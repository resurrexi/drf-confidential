from rest_framework import serializers

from drf_confidential.mixins import ConfidentialFieldsMixin

from .models import Employee, Profile, EmployeeJob, Post


class EmployeeSerializer(ConfidentialFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        confidential_fields = (
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


class EmployeeJobSerializer(
    ConfidentialFieldsMixin, serializers.ModelSerializer
):
    class Meta:
        model = EmployeeJob
        fields = "__all__"
        confidential_fields = ("salary",)
        confidential_permission = "view_employee_salary"


class PostSerializer(ConfidentialFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
        confidential_fields = ("secret_note",)
