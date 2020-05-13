from collections import OrderedDict
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject


class PrivateFieldsMixin:
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
            return PrivateFieldsMixin._resolve_lookups(new_instance, lookups)
        return new_instance

    def _check_exposure(self, instance):
        """Run check against the request user to determine exposure.

        Evaluates user's permission to view the model instance's private
        fields, or ownership, or self.
        """
        app_label = instance._meta.app_label
        model_name = instance._meta.model_name
        private_permission = f"{app_label}.view_sensitive_{model_name}"
        user_link = getattr(self.Meta, "user_relation", None)

        try:
            user = self.context.get("request").user
        except AttributeError:
            user = None

        if user is not None:
            if user.has_perm(private_permission):
                return True
            if instance == user:
                return True
            if getattr(instance, "created_by", None) == user:
                return True
            if user_link:
                field_lookups = user_link.split("__")
                return self._resolve_lookups(instance, field_lookups) == user
        return False

    def to_representation(self, instance):
        """Deserialize object instance to dict of primitive datatypes.

        The resulting data depends on the user's permission on the
        model instance. If the user does not have the permission, then
        the private fields are withheld. Otherwise, they will be shown.
        """
        ret = OrderedDict()
        fields = self._readable_fields
        expose = self._check_exposure(instance)

        if not expose:
            fields = [
                field
                for field in self._readable_fields
                if field.field_name not in getattr(self.Meta, "private_fields")
            ]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that
            # fields do not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need
            # to resolve the pk value.
            check_for_none = (
                attribute.pk
                if isinstance(attribute, PKOnlyObject)
                else attribute
            )
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret
