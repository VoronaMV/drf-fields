import six
import pytz
import datetime
from django.utils.encoding import smart_text
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class RecursiveField(serializers.Serializer):
    """
    Field for recursive tree scaling with set depth.
    many=True should be passed
    :param max_depth: int - depth of tree should be passed, None causes to full tree scaling
    """
    def __init__(self, *args, **kwargs):
        self._max_depth = kwargs.pop('max_depth', None)
        self._recurse_lvl = 1
        self._recurse_many = kwargs.pop('many', False)

        super().__init__(**kwargs)

    def to_representation(self, value):
        parent = self.parent  # parent is parent serializer instance
        if isinstance(parent, serializers.ListSerializer):
            parent = parent.parent

        lvl = getattr(parent, '_recurse_lvl', 1)
        max_lvl = self._max_depth or getattr(parent, '_recurse_max', None)

        serializer_class = parent.__class__

        if not max_lvl or lvl <= max_lvl:
            serializer = serializer_class(
                value, many=self._recurse_many, context=self.context)

            serializer._recurse_lvl = lvl + 1
            serializer._max_depth = max_lvl

            return serializer.data
        else:

            return value.id


class TimestampField(serializers.Field):
    """
    Convert a django datetime to/from timestamp.
    """

    def to_representation(self, value):
        """
        Convert the field to its internal representation (aka timestamp)
        :param value: the DateTime value
        :return: a UTC timestamp integer
        """
        request = self.context.get('request')
        if not request:
            return value.timestamp()
        try:
            user_timezone_text = request.user.timezone
        except AttributeError:
            user_timezone_text = 'UTC'
        user_timezone = pytz.timezone(user_timezone_text)
        ts = value.astimezone(user_timezone).timestamp()
        return ts

    def to_internal_value(self, value):
        """
        deserialize a timestamp to a DateTime value
        :param value: the timestamp value
        :return: a django DateTime value
        """
        converted = datetime.datetime.fromtimestamp(float('%s' % value))
        return converted


class TimestampFromDateField(TimestampField):
    """
    Convert a django date to/from timestamp.
    """

    def to_representation(self, value):
        """
        Convert the field to its internal representation (aka timestamp)
        :param value: the Date value
        :return: a UTC timestamp integer
        """
        _datetime = datetime.datetime.combine(value, datetime.time.min)
        ts = _datetime.timestamp()
        return ts


class NaturalChoiceField(serializers.ChoiceField):
    """
    Choice field that really get receives and validates
    values for external representation that defined in choices
    and convert it for internal values defined in choices.
    And do the opposite action too.
    Other behavior is totally the same as in ChoiceField.

    Usage:
        CHOICES = (("internal", "external"), )
        field = NaturalChoiceField(choices=CHOICES)

        field.to_representation("internal")
        >> "external"
        field.to_representation("external")
        >> "external"

        field.to_internal_value("external")
        >> "internal"
        field.to_internal_value("internal")
        >> ValidationError: [ErrorDetail(...)]

    """

    def to_internal_value(self, data):
        """
        Overwritten .to_internal_value() of ChoiceField.
        Changed behaviour in try: ... block of code. Originally
        it returns `self.choice_strings_to_values[six.text_type(data)]`.
        :param data:
        :return: internal representation of external value from choices
                 or raise ValidationError
        """
        if data == '' and self.allow_blank:
            return ''
        try:
            for internal, external in self.choice_strings_to_values.items():
                if external == data:
                    return internal
            else:
                raise KeyError
        except KeyError:
            self.fail('invalid_choice', input=data)

    def _get_choices(self):
        return self._choices

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, choices):
        # Map the string representation of choices to the underlying value.
        # Allows us to deal with eg. integer choices while supporting either
        # integer or string input, but still get the correct datatype out.
        super()._set_choices(choices)
        self.choice_strings_to_values = {
            key: val for key, val in self.choices.items()
        }

    def to_representation(self, value):
        if value in ('', None):
            return value
        return self.choice_strings_to_values.get(value, value)


class GetOrCreateSlugRelatedField(serializers.SlugRelatedField):
    """
    A SlugRelatedField that make possible either to create relations
    between objects that has already exists and which should be created.
    """

    def __init__(self, slug_field=None, get_or_create=True, **kwargs):
        self.get_or_create = get_or_create
        super().__init__(slug_field, **kwargs)

    def do_action(self, data):
        queryset = self.get_queryset()
        action = 'get_or_create' if self.get_or_create else 'get'
        attr = getattr(queryset, action)
        if action == 'get':
            return attr(**{self.slug_field: data})
        else:
            return attr(**{self.slug_field: data})[0]

    def to_internal_value(self, data):
        """
        Overwritten parent method in `try` block to make possible perform
         `get` or `get_or_create` action.
        """
        try:
            return self.do_action(data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
        except (TypeError, ValueError):
            self.fail('invalid')
