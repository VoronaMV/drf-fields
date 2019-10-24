import pytest
from rest_framework import serializers
from drf_fields.fields import NaturalChoiceField


class TestNaturalChoiceField:

    def test_to_representation(self, choices_with_serializer):
        choices, Serializer = choices_with_serializer
        choice, *_ = choices
        internal_repr, external_repr = choice
        data = {"field": internal_repr}
        result = Serializer().to_representation(data)
        assert result['field'] == external_repr

    def test_to_internal_value(self, choices_with_serializer):
        choices, Serializer = choices_with_serializer
        choice, *_ = choices
        internal_repr, external_repr = choice
        data = {"field": external_repr}
        obj = Serializer(data=data)
        obj.is_valid(raise_exception=True)
        assert obj.validated_data['field'] == internal_repr
