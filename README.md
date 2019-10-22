# Django REST framework extra fields

## Project description
Serializer fields that don't exist in [Django REST framework](https://github.com/encode/django-rest-framework) but 
can be useful in some cases.

## Table of contents
- [Compatibility](#compatibility)
- [Installation](#installation)
- [Fields description](#fields-description)
  - [NaturalChoiceField](#fields-description)
## Compatibility
All fields were tested and applied in projects with:
  - `python>=3.6`
  - `Django>=2.0`
  - `djangorestframework>=3.9`

## Installation
`pip install git+https://github.com/VoronaMV/drf-fields.git`

## Fields description

This is short documentation about each field.

### NaturalChoiceField

This field extends `rest_framework.serializers.ChoiceField`.
The native DRF ChoiceField doesn't returns real model or field choices
in representation, especially when representation and internal representation
have different types.

This field make possible to retrieve `to_representation` choice that defined.

For example, you have `models.py` file:
```python
from django.db import models


class Person(models.Model):
    SEX_CHOICES = (
        ('male', 1),
        ('female', 2),
    )    

    name = models.CharField(max_length=255)
    sex = models.IntegerField(choices=SEX_CHOICES)
```

And `serializers.py`
```python
from rest_framework import serializers
from drf_fields import NaturalChoiceField
from myapp.models import Person


class PersonSerializerNaturalChoiceField(serializers.ModelSerializer):
    
    sex = NaturalChoiceField(choices=Person.SEX_CHOICES)
    
    class Meta:
        model = Person
        fields = ('name', 'sex')

class PersonSerializerWithDRFChoiceField(serializers.ModelSerializer):
    
    sex = serializers.ChoiceField(choices=Person.SEX_CHOICES)
    
    class Meta:
        model = Person
        fields = ('name', 'sex')
```

Compare representation of this 2 serializer:
```shell script

```