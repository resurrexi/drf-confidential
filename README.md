# drf-confidential

[![Build Status](https://travis-ci.org/resurrexi/drf-confidential.svg?branch=master)](https://travis-ci.org/resurrexi/drf-confidential)
[![codecov](https://codecov.io/gh/resurrexi/drf-confidential/branch/master/graph/badge.svg)](https://codecov.io/gh/resurrexi/drf-confidential)

**drf-confidential** is a package to help you control how a model's sensitive data is shared across your API.

## Installation

```bash
pip install drf-confidential
```

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

Every field except for `first_name` and `last_name` in the `Employee` model is considered sensitive data. This means that only the `Profile` user with the linked `employee_profile`, or a user with elevated privileges (e.g. an admin or HR staff), can access those fields.


Unfortunately, there is no simple way to control permissions down to the field level in DRF. Enter **drf-confidential**.

## drf-confidential in action

Let's suppose there are 2 users:

* *amazhong* is just a regular user without elevated privileges
* *googe* is a staff/admin with elevated privileges

### What happens when they make a GET request on the `Employee` list endpoint?

<table>
<thead>
<tr><td colspan="2">GET /api/employees/</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
200 OK

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "first_name": "Ama",
            "last_name": "Zhong",
            "address_1": "440 Terry Ave N",
            "address_2": "",
            "country": "US",
            "city": "Seattle",
            "phone_number": "+12062661000"
        },
        {
            "id": 2,
            "first_name": "Goo",
            "last_name": "Ge"
        }
    ]
}
```

</td>
<td>

```json
200 OK

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "first_name": "Ama",
            "last_name": "Zhong",
            "address_1": "440 Terry Ave N",
            "address_2": "",
            "country": "US",
            "city": "Seattle",
            "phone_number": "+12062661000"
        },
        {
            "id": 2,
            "first_name": "Goo",
            "last_name": "Ge",
            "address_1": "1600 Amphitheatre Pkwy",
            "address_2": "",
            "country": "US",
            "city": "Mountain View",
            "phone_number": "+16502530000"
        }
    ]
}
```

</td>
</tr>
</tbody>
</table>

### What about GET requests at the detail level?

<table>
<thead>
<tr><td colspan="2">GET /api/employees/1/</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
200 OK

{
    "id": 1,
    "first_name": "Ama",
    "last_name": "Zhong",
    "address_1": "440 Terry Ave N",
    "address_2": "",
    "country": "US",
    "city": "Seattle",
    "phone_number": "+12062661000"
}
```

</td>
<td>

```json
200 OK

{
    "id": 1,
    "first_name": "Ama",
    "last_name": "Zhong",
    "address_1": "440 Terry Ave N",
    "address_2": "",
    "country": "US",
    "city": "Seattle",
    "phone_number": "+12062661000"
}
```

</td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr><td colspan="2">GET /api/employees/2/</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
200 OK

{
    "id": 2,
    "first_name": "Goo",
    "last_name": "Ge"
}
```

</td>
<td>

```json
200 OK

{
    "id": 2,
    "first_name": "Goo",
    "last_name": "Ge",
    "address_1": "1600 Amphitheatre Pkwy",
    "address_2": "",
    "country": "US",
    "city": "Mountain View",
    "phone_number": "+16502530000"
}
```

</td>
</tr>
</tbody>
</table>

### What about create?

<table>
<thead>
<tr><td colspan="2">
POST /api/employees/

```json
{
    "first_name": "Ah",
    "last_name": "Poh",
    "address_1": "One Apple Park Way",
    "address_2": "",
    "country": "US",
    "city": "Cupertino",
    "phone_number": "+14089961010"
}
```

</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
403 FORBIDDEN
```

</td>
<td>

```json
201 CREATED

{
    "id": 3,
    "first_name": "Ah",
    "last_name": "Poh",
    "address_1": "One Apple Park Way",
    "address_2": "",
    "country": "US",
    "city": "Cupertino",
    "phone_number": "+14089961010"
}
```

</td>
</tr>
</tbody>
</table>

### And update?

<table>
<thead>
<tr><td colspan="2">
PATCH /api/employees/1/

```json
{
    "address_1": "123 New Drive",
    "phone_number": "+13214567890"
}
```

</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
200 OK

{
    "id": 1,
    "first_name": "Ama",
    "last_name": "Zhong",
    "address_1": "123 New Drive",
    "address_2": "",
    "country": "US",
    "city": "Seattle",
    "phone_number": "+13214567890"
}
```

</td>
<td>

```json
200 OK

{
    "id": 1,
    "first_name": "Ama",
    "last_name": "Zhong",
    "address_1": "123 New Drive",
    "address_2": "",
    "country": "US",
    "city": "Seattle",
    "phone_number": "+13214567890"
}
```

</td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr><td colspan="2">
PATCH /api/employees/2/

```json
{
    "address_1": "123 New Drive",
    "phone_number": "+13214567890"
}
```

</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
403 FORBIDDEN
```

</td>
<td>

```json
200 OK

{
    "id": 2,
    "first_name": "Goo",
    "last_name": "Ge",
    "address_1": "123 New Drive",
    "address_2": "",
    "country": "US",
    "city": "Mountain View",
    "phone_number": "+13214567890"
}
```

</td>
</tr>
</tbody>
</table>

### And delete?

<table>
<thead>
<tr><td colspan="2">DELETE /api/employees/1/</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
204 NO CONTENT
```

</td>
<td>

```json
204 NO CONTENT
```

</td>
</tr>
</tbody>
</table>

<table>
<thead>
<tr><td colspan="2">DELETE /api/employees/2/</td></tr>
</thead>
<tbody>
<tr><td>amazhong</td><td>googe</td></tr>
<tr>
<td>

```json
403 FORBIDDEN
```

</td>
<td>

```json
204 NO CONTENT
```

</td>
</tr>
</tbody>
</table>

## Basic usage

### Step 1

Create a confidential permission on your model and `python manage.py migrate`.

```python
class Employee(models.Model):
    ...  # fields defined earlier above

    class Meta:
        permissions = (
            ("view_sensitive_employee", "Can view employees' sensitive data"),
        )
```

### Step 2

Add the `ConfidentialFieldsMixin` to your serializer and define your `confidential_fields` and `user_relation` lookup.

```python
from rest_framework import serializers

from drf_confidential.mixins import ConfidentialFieldsMixin


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
```

`ConfidentialFieldsMixin` is configured to look for cases where either the request user is the model instance, the request user owns the model instance, the request user has a relation to the model instance, or the request user has the elevated permissions. The `confidential_fields` meta attribute specifies which fields are considered sensitive. The `user_relation` lookup specifies the relation of the model to the user model. In the [model definitions above](#Motivation), the relation to the `Profile` model from the `Employee` model is through the back-reference, `login_account`.

### Step 3

Add the `ConfidentialFieldsPermission` as a permission class to the viewset.

```python
from rest_framework.viewsets import ModelViewSet

from drf_confidential.permissions import ConfidentialFieldsPermission


class EmployeeViewSet(ModelViewSet):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [
        ...  # your default permissions, e.g. IsAuthenticated
        ConfidentialFieldsPermission
    ]
```

The permission follows the logic that a user must have either elevated permissions, have ownership, or have a relation to the model instance if they want to `update`, `partial_update`, or `delete`. For `create`, only users with elevated permissions are allowed. For `retrieve` and `list`, all users are allowed.
