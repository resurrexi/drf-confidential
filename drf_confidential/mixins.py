from django.conf import settings

permission_template = getattr(
    settings,
    "CONFIDENTIAL_PERMISSION_TEMPLATE",
    "view_sensitive_{model_name}",
)
ownership_field = getattr(
    settings, "CONFIDENTIAL_OWNERSHIP_FIELD", "created_by"
)


class ConfidentialFieldsMixin:
    @staticmethod
    def _resolve_lookups(instance, lookups):
        """Traverse across the instance's relationship.

        Recursively resolve the relationship fields in the lookups list
        and return the final model instance when traversals have
        exhausted.
        """
        field = lookups.pop(0)
        if hasattr(instance, field):
            new_instance = getattr(instance, field)
        else:
            return None
        if len(lookups) > 0:
            return ConfidentialFieldsMixin._resolve_lookups(
                new_instance, lookups
            )
        return new_instance

    def _check_exposure(self, instance):
        """Run check against the request user to determine exposure.

        Evaluates user's permission to view the model instance's
        confidential fields, or ownership, or self.
        """
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        confidential_permission = (
            app_label
            + "."
            + getattr(
                self.Meta, "confidential_permission", permission_template
            ).format(model_name=model_name)
        )
        user_link = getattr(self.Meta, "user_relation", None)

        user = getattr(self.context.get("request"), "user", None)

        if user is not None:
            if user.has_perm(confidential_permission):
                return True
            if instance == user:
                return True
            if getattr(instance, ownership_field, None) == user:
                return True
            if user_link:
                field_lookups = user_link.split("__")
                return self._resolve_lookups(instance, field_lookups) == user
        return False

    def to_representation(self, instance):
        """Override deserialization method.

        The resulting data depends on the user's permission on the
        model instance. If the user does not have the permission, then
        the confidential fields are withheld. Otherwise, they will be
        shown.
        """
        ret = super().to_representation(instance)
        expose = self._check_exposure(instance)

        if not expose:
            for field in getattr(self.Meta, "confidential_fields"):
                del ret[field]

        return ret
