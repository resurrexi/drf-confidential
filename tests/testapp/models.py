from django.contrib.auth.models import AbstractUser
from django.db import models


class Employee(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address_1 = models.CharField(max_length=256)
    address_2 = models.CharField(max_length=256, blank=True)
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)

    class Meta:
        permissions = (
            ("view_sensitive_employee", "Can view sensitive employee info"),
        )


class Profile(AbstractUser):
    employee_profile = models.OneToOneField(
        Employee,
        null=True,
        on_delete=models.SET_NULL,
        related_name="login_account",
    )

    class Meta:
        permissions = (
            ("view_sensitive_profile", "Can view sensitive profile info"),
        )


class EmployeeJob(models.Model):
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, related_name="job"
    )
    job_title = models.CharField(max_length=64)
    salary = models.IntegerField()

    class Meta:
        permissions = (
            ("view_employee_salary", "Can view job salaries of employees"),
        )


class Post(models.Model):
    post_title = models.CharField(max_length=64)
    post_content = models.TextField()
    secret_note = models.CharField(max_length=64)
    created_by = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="posts"
    )

    class Meta:
        permissions = (
            ("view_sensitive_post", "Can view secret notes on posts"),
        )
