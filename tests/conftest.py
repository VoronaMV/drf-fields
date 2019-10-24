import pytest
from rest_framework import serializers
from drf_fields.fields import NaturalChoiceField


@pytest.fixture(
    params=[
        ((1, "external_repr"), ),
        (("internal_repr", 1), ),
        (("internal_repr", 1), "external_repr"),
        ((1, 1), ),
        (('', ''), ),
        ((1.1, 'external_repr'), ),
        (("internal_repr", 1.1), ),
    ]
)
def choices_with_serializer(request):
    class ChoiceSerializer(serializers.Serializer):
        CHOICES = request.param
        field = NaturalChoiceField(choices=CHOICES)

    yield request.param, ChoiceSerializer
