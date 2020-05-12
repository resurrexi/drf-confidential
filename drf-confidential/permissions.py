from rest_framework.permissions import BasePermission


class PrivateFieldsPermission(BasePermission):
    def has_permission(self, request, view):
        app_label = view.get_serializer().Meta.model._meta.app_label
        model_name = view.get_serializer().Meta.model._meta.model_name
        private_permission = f"{app_label}.view_sensitive_{model_name}"

        # A user without the private permission should still be able
        # to list/update/delete records if the record is self or
        # self-owned. Therefore, these actions should be allowed for
        # the user even if the user does't have the private permission.
        if view.action == "create":
            return request.user.has_perm(private_permission)
        return True

    def has_object_permission(self, request, view, obj):
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name
        private_permission = f"{app_label}.view_sensitive_{model_name}"
        user_link = getattr(view.get_serializer().Meta, "user_relation", None)

        # Any user should be allowed to use the retrieve action, due to
        # the serializer determining which fields to expose.
        if view.action == "retrieve":
            return True
        if request.user.has_perm(private_permission):
            return True
        if obj == request.user:
            return True
        if user_link:
            return getattr(obj, user_link, None) == request.user
        return False
