from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.utils.crypto import get_random_string

from rest_framework.test import APITestCase
from rest_framework import status

from tests.testapp.models import Employee, Profile, EmployeeJob, Post

_USER_MODEL = get_user_model()
_USER1 = {
    "username": "testuser1",
    "email": "user1@domain.com",
    "password": "Test!@#$5",
}
_USER2 = {
    "username": "testuser2",
    "email": "user2@domain.com",
    "password": "Test!@#$5",
}
_USER3 = {
    "username": "testuser3",
    "email": "user3@domain.com",
    "password": "Test!@#$5",
}


class EmployeeAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create users
        cls.user1 = _USER_MODEL.objects.create_user(**_USER1)
        cls.user2 = _USER_MODEL.objects.create_user(**_USER2)
        cls.user3 = _USER_MODEL.objects.create_user(**_USER3)

        # create employee profiles for users
        cls.employee1 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        cls.employee2 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        cls.employee3 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        cls.employee4 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )

        # map employee profiles to users
        cls.user1.employee_profile = cls.employee1
        cls.user1.save()
        cls.user2.employee_profile = cls.employee2
        cls.user2.save()
        cls.user3.employee_profile = cls.employee3
        cls.user3.save()

        # set confidential permissions for users
        confidential_perm = Permission.objects.get(
            codename="view_sensitive_employee"
        )
        cls.user3.user_permissions.add(confidential_perm)

    def setUp(self):
        self.list_name = "employee-list"
        self.detail_name = "employee-detail"

    def test_get_list_for_anonymous(self):
        self.client.force_authenticate(user=None)

        # can get list
        response = self.client.get(reverse(self.list_name))
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 4)

        # all employees' sensitive data hidden
        private_flags = [
            1 if "address_1" in result.keys() else 0
            for result in response.data
        ]
        self.assertEqual(sum(private_flags), 0)

    def test_get_list_for_user1(self):
        self.client.force_authenticate(user=self.user1)

        # can get list
        response = self.client.get(reverse(self.list_name))
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 4)

        # only the user's records show sensitive data
        private_flags = [
            1 if "address_1" in result.keys() else 0
            for result in response.data
        ]
        self.assertEqual(sum(private_flags), 1)
        address_2 = response.data[0]["address_2"]
        self.assertEqual(address_2, self.employee1.address_2)

    def test_get_list_for_user2(self):
        self.client.force_authenticate(user=self.user2)

        # can get list
        response = self.client.get(reverse(self.list_name))
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 4)

        # only the user's records show sensitive data
        private_flags = [
            1 if "address_2" in result.keys() else 0
            for result in response.data
        ]
        self.assertEqual(sum(private_flags), 1)
        country = response.data[1]["country"]
        self.assertEqual(country, self.employee2.country)

    def test_get_list_for_user3(self):
        self.client.force_authenticate(user=self.user3)

        # can get list
        response = self.client.get(reverse(self.list_name))
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.data), 4)

        # user can view sensitive records for all employees
        private_flags = [
            1 if "phone_number" in result.keys() else 0
            for result in response.data
        ]
        self.assertTrue(all(i == 1 for i in private_flags))
        city = response.data[0]["city"]
        self.assertEqual(city, self.employee1.city)
        phone_number = response.data[1]["phone_number"]
        self.assertEqual(phone_number, self.employee2.phone_number)
        address_1 = response.data[2]["address_1"]
        self.assertEqual(address_1, self.employee3.address_1)
        country = response.data[3]["country"]
        self.assertEqual(country, self.employee4.country)

    def test_get_detail_for_anonymous(self):
        self.client.force_authenticate(user=None)

        # employees' sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("address_1", response.data.keys())
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("address_2", response.data.keys())
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("country", response.data.keys())
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("city", response.data.keys())

    def test_get_detail_for_user1(self):
        self.client.force_authenticate(user=self.user1)

        # employee1 sensitive data shown
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["address_1"], self.employee1.address_1)

        # employee2 sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("address_2", response.data.keys())

        # employee3 sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("city", response.data.keys())

        # employee4 sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("country", response.data.keys())

    def test_get_detail_for_user2(self):
        self.client.force_authenticate(user=self.user2)

        # employee1 sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("phone_number", response.data.keys())

        # employee2 sensitive data shown
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["address_2"], self.employee2.address_2)

        # employee3 sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("address_1", response.data.keys())

        # employee4 sensitive data hidden
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("phone_number", response.data.keys())

    def test_get_detail_for_user3(self):
        self.client.force_authenticate(user=self.user3)

        # employee1 sensitive data shown
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["address_2"], self.employee1.address_2)

        # employee2 sensitive data shown
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["city"], self.employee2.city)

        # employee3 sensitive data shown
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["address_1"], self.employee3.address_1)

        # employee4 sensitive data shown
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["country"], self.employee4.country)

    def test_create_for_user1_should_fail(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            reverse(self.list_name),
            {
                "first_name": "John",
                "last_name": "Smith",
                "address_1": "123 Test Drive",
                "address_2": "Unit A",
                "city": "New York",
                "country": "USA",
                "phone_number": "1111111111",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_for_user2_should_fail(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.post(
            reverse(self.list_name),
            {
                "first_name": "John",
                "last_name": "Smith",
                "address_1": "123 Test Drive",
                "address_2": "Unit A",
                "city": "New York",
                "country": "USA",
                "phone_number": "1111111111",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_for_user3_should_succeed(self):
        self.client.force_authenticate(user=self.user3)
        response = self.client.post(
            reverse(self.list_name),
            {
                "first_name": "John",
                "last_name": "Smith",
                "address_1": "123 Test Drive",
                "address_2": "Unit A",
                "city": "New York",
                "country": "USA",
                "phone_number": "1111111111",
            },
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn("first_name", response.data)
        self.assertEqual(response.data["city"], "New York")
        self.assertEqual(response.data["country"], "USA")

    def test_update_for_user1(self):
        self.client.force_authenticate(user=self.user1)

        # should succeed when updating employee1
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk}),
            {"first_name": "George", "address_1": "123 Liberty Drive"},
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["first_name"], "George")
        self.assertEqual(response.data["address_1"], "123 Liberty Drive")

        # should fail when updating employee2
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk}),
            {"first_name": "George", "address_1": "123 Liberty Drive"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should fail when updating employee3
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk}),
            {"first_name": "George", "address_1": "123 Liberty Drive"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should fail when updating employee4
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk}),
            {"first_name": "George", "address_1": "123 Liberty Drive"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_for_user2(self):
        self.client.force_authenticate(user=self.user2)

        # should fail when updating employee1
        response = self.client.put(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk}),
            {
                "first_name": "George",
                "last_name": "Washington",
                "address_1": "123 Liberty Drive",
                "address_2": "",
                "city": "Washington DC",
                "country": "USA",
                "phone_number": "07041776",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should succeed when updating employee2
        response = self.client.put(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk}),
            {
                "first_name": "George",
                "last_name": "Washington",
                "address_1": "123 Liberty Drive",
                "address_2": "",
                "city": "Washington DC",
                "country": "USA",
                "phone_number": "07041776",
            },
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["first_name"], "George")
        self.assertEqual(response.data["last_name"], "Washington")
        self.assertEqual(response.data["address_1"], "123 Liberty Drive")
        self.assertEqual(response.data["address_2"], "")
        self.assertEqual(response.data["city"], "Washington DC")
        self.assertEqual(response.data["country"], "USA")
        self.assertEqual(response.data["phone_number"], "07041776")

        # should fail when updating employee3
        response = self.client.put(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk}),
            {
                "first_name": "George",
                "last_name": "Washington",
                "address_1": "123 Liberty Drive",
                "address_2": "",
                "city": "Washington DC",
                "country": "USA",
                "phone_number": "07041776",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should fail when updating employee4
        response = self.client.put(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk}),
            {
                "first_name": "George",
                "last_name": "Washington",
                "address_1": "123 Liberty Drive",
                "address_2": "",
                "city": "Washington DC",
                "country": "USA",
                "phone_number": "07041776",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_for_user3(self):
        self.client.force_authenticate(user=self.user3)

        # should succeed when updating employee1
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk}),
            {"first_name": "George", "address_1": "123 Liberty Drive"},
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["first_name"], "George")
        self.assertEqual(response.data["address_1"], "123 Liberty Drive")

        # should succeed when updating employee2
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk}),
            {"last_name": "Adams", "city": "Anaheim"},
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["last_name"], "Adams")
        self.assertEqual(response.data["city"], "Anaheim")

        # should succeed when updating employee3
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk}),
            {"country": "France", "phone_number": "12345678"},
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["country"], "France")
        self.assertEqual(response.data["phone_number"], "12345678")

        # should succeed when updating employee4
        response = self.client.patch(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk}),
            {"address_2": "Bldg 1 Fl 32"},
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["address_2"], "Bldg 1 Fl 32")

    def test_delete_for_user1(self):
        self.client.force_authenticate(user=self.user1)

        # should succeed when deleting employee1
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))

        # should fail when deleting employee2
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should fail when deleting employee3
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should fail when deleting employee4
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_for_user2(self):
        self.client.force_authenticate(user=self.user2)

        # should fail when deleting employee1
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should succeed when deleting employee2
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))

        # should fail when deleting employee3
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # should fail when deleting employee4
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_for_user3(self):
        self.client.force_authenticate(user=self.user3)

        # should succeed when deleting employee1
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))

        # should succeed when deleting employee2
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))

        # should succeed when deleting employee3
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee3.pk})
        )
        self.assertTrue(status.is_success(response.status_code))

        # should succeed when deleting employee4
        response = self.client.delete(
            reverse(self.detail_name, kwargs={"pk": self.employee4.pk})
        )
        self.assertTrue(status.is_success(response.status_code))


class ProfileAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create users
        cls.user1 = _USER_MODEL.objects.create_user(**_USER1)
        cls.user2 = _USER_MODEL.objects.create_user(**_USER2)
        cls.user3 = _USER_MODEL.objects.create_user(**_USER3)

        # create employee profiles for users
        cls.employee1 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        cls.employee2 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        cls.employee3 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        cls.employee4 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )

        # map employee profiles to users
        cls.user1.employee_profile = cls.employee1
        cls.user1.save()
        cls.user2.employee_profile = cls.employee2
        cls.user2.save()
        cls.user3.employee_profile = cls.employee3
        cls.user3.save()

        # set confidential permissions for users
        confidential_perm = Permission.objects.get(
            codename="view_sensitive_employee"
        )
        cls.user3.user_permissions.add(confidential_perm)

    def setUp(self):
        self.list_name = "profile-list"
        self.detail_name = "profile-detail"

    def test_get_list_confidential_still_applies_on_nested_relation(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse(self.list_name))
        private_flags = [
            1 if "country" in result["employee_profile"].keys() else 0
            for result in response.data
        ]
        self.assertEqual(sum(private_flags), 1)

        self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse(self.list_name))
        private_flags = [
            1 if "address_1" in result["employee_profile"].keys() else 0
            for result in response.data
        ]
        self.assertEqual(sum(private_flags), 1)

        self.client.force_authenticate(user=self.user3)
        response = self.client.get(reverse(self.list_name))
        private_flags = [
            1 if "phone_number" in result["employee_profile"].keys() else 0
            for result in response.data
        ]
        self.assertTrue(all(i == 1 for i in private_flags))

    def test_sensitive_data_shows_for_self(self):
        self.client.force_authenticate(user=self.user1)

        # self
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.user1.pk})
        )
        self.assertIn("email", response.data.keys())

        # other
        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.user2.pk})
        )
        self.assertNotIn("email", response.data.keys())


class EmployeeJobAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create users
        cls.user1 = _USER_MODEL.objects.create_user(**_USER1)
        cls.user2 = _USER_MODEL.objects.create_user(**_USER2)

        # create employee profiles for users
        employee1 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )
        employee2 = Employee.objects.create(
            first_name=get_random_string(length=5),
            last_name=get_random_string(length=5),
            address_1=get_random_string(length=16),
            address_2=get_random_string(length=16),
            country=get_random_string(length=16),
            city=get_random_string(length=16),
            phone_number=get_random_string(length=16),
        )

        # map employee profiles to users
        cls.user1.employee_profile = employee1
        cls.user1.save()
        cls.user2.employee_profile = employee2
        cls.user2.save()

        # create employee jobs
        cls.job1 = EmployeeJob.objects.create(
            employee=employee1,
            job_title=get_random_string(length=8),
            salary=10000,
        )
        cls.job2 = EmployeeJob.objects.create(
            employee=employee2,
            job_title=get_random_string(length=8),
            salary=20000,
        )

        # set confidential permissions for users
        confidential_perm = Permission.objects.get(
            codename="view_employee_salary"
        )
        cls.user2.user_permissions.add(confidential_perm)

    def setUp(self):
        self.list_name = "employeejob-list"
        self.detail_name = "employeejob-detail"

    def test_custom_permission_is_used(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.job1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["salary"], self.job1.salary)

    def test_deep_user_relation_is_resolved(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.job1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data["salary"], self.job1.salary)

        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.job2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("salary", response.data)


class PostAPITest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create users
        cls.user1 = _USER_MODEL.objects.create_user(**_USER1)
        cls.user2 = _USER_MODEL.objects.create_user(**_USER2)

        # create posts
        cls.post1 = Post.objects.create(
            post_title=get_random_string(length=16),
            post_content=get_random_string(length=32),
            secret_note=get_random_string(length=16),
            created_by=cls.user1,
        )
        cls.post2 = Post.objects.create(
            post_title=get_random_string(length=16),
            post_content=get_random_string(length=32),
            secret_note=get_random_string(length=16),
            created_by=cls.user2,
        )

        # set confidential permissions for users
        confidential_perm = Permission.objects.get(
            codename="view_sensitive_post"
        )
        cls.user2.user_permissions.add(confidential_perm)

    def setUp(self):
        self.detail_name = "post-detail"

    def test_hide_sensitive_fields_if_not_owner(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.post2.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertNotIn("secret_note", response.data)

    def test_show_sensitive_fields_for_elevated_user(self):
        self.client.force_authenticate(user=self.user2)

        response = self.client.get(
            reverse(self.detail_name, kwargs={"pk": self.post1.pk})
        )
        self.assertTrue(status.is_success(response.status_code))
        self.assertIn("secret_note", response.data)
        self.assertEqual(response.data["secret_note"], self.post1.secret_note)
