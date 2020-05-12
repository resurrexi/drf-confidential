# drf-confidential

**drf-confidential** is a package to help you control how a model's sensitive data is shared across your API.

## Motivation

Imagine you have the following models declared as:

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class Profile(AbstractUser):
    email = models.EmailField(unique=True)
    employee_profile = models.OneToOneField(
        "Employee",
        null=True,
        on_delete=models.PROTECT,
        related_name='login_account'
    )


class Employee(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    address_1 = models.CharField(max_length=256)
    address_2 = models.CharField(max_length=256, blank=True)
    country = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=16)
```

Every field except for `first_name` and `last_name` in the *Employee* model is considered sensitive data. This means that only the *Profile* user with the linked `employee_profile`, or a user with elevated privileges (e.g. an admin or HR staff), can access those fields.

Unfortunately, vanilla DRF does not have the capability to control permissions down to the field level. Enter **drf-confidential**.
