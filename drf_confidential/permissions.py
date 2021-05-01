from django.conf import settings

from rest_framework.permissions import BasePermission

from .mixins import ConfidentialFieldsMixin

permission_template = getattr(
    settings,
    "CONFIDENTIAL_PERMISSION_TEMPLATE",
    "view_sensitive_{model_name}",
)


class ConfidentialFieldsPermission(BasePermission):
    def has_permission(self, request, view):
        serializer = view.get_serializer()
        app_label = serializer.Meta.model._meta.app_label
        model_name = serializer.Meta.model._meta.model_name
        confidential_permission = (
            app_label
            + "."
            + getattr(
                serializer.Meta, "confidential_permission", permission_template
            ).format(model_name=model_name)
        )

        # A user without the confidential permission should still be
        # able to list/update/delete records if the record is self or
        # self-owned. Therefore, these actions should be allowed for
        # the user even if the user does't have the confidential
        # permission.
        if view.action == "create":
            return request.user.has_perm(confidential_permission)
        return True

    def has_object_permission(self, request, view, obj):
        serializer = view.get_serializer()
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        confidential_permission = (
            app_label
            + "."
            + getattr(
                serializer.Meta, "confidential_permission", permission_template
            ).format(model_name=model_name)
        )
        user_link = getattr(serializer.Meta, "user_relation", None)

        # Any user should be allowed to use the retrieve action, due to
        # the serializer determining which fields to expose.
        if view.action == "retrieve":
            return True
        if request.user.has_perm(confidential_permission):
            return True
        if obj == request.user:
            return True
        if user_link:
            field_lookups = user_link.split("__")
            return (
                ConfidentialFieldsMixin._resolve_lookups(obj, field_lookups)
                == request.user
            )
        return False
