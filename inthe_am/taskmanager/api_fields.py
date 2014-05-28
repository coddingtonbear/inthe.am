from uuid import UUID

from tastypie.fields import ApiField


class UUIDField(ApiField):
    """
    A date field.
    """
    dehydrated_type = 'date'
    help_text = 'A date as a string. Ex: "2010-11-10"'

    def convert(self, value):
        if value is None:
            return None

        return value

    def hydrate(self, bundle):
        value = super(UUIDField, self).hydrate(bundle)

        if value and not isinstance(value, UUID):
            value = UUID(value)

        return value
