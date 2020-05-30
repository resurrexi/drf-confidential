from rest_framework.routers import SimpleRouter

from .views import (
    EmployeeViewSet,
    ProfileViewSet,
    EmployeeJobViewSet,
    PostViewSet,
)


router = SimpleRouter()
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"employeejobs", EmployeeJobViewSet, basename="employeejob")
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = router.urls
