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
The native DRF ChoiceField doesn't return real model or field choices
in representation, especially when representation and internal representation
have different types.

This field make possible to retrieve `to_representation` choice that defined.

For example, you have `models.py` file:
```python
from django.db import models


class Person(models.Model):
    MALE = 1
    FEMALE = 2
    SEX_CHOICES = (
        (MALE, 'male'),
        (FEMALE, 'female'),
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

Compare representation of this 2 serializer in ipython console:
```

In [1]: from myapp.models import Person                                                                                                                            

In [2]: from myapp.serializers import PersonSerializerNaturalChoiceField, PersonSerializerWithDRFChoiceField                                                       

# Creating 2 person objects

In [3]: bob = Person.objects.create(name='Bob', sex=Person.MALE)                                                                                                   

In [4]: ann = Person.objects.create(name='Ann', sex=Person.FEMALE)                                                                                                 

# Check that DB values really saved as numeric

In [5]: bob.sex, ann.sex                                                                                                                                           
Out[5]: (1, 2)

# What returns native DRF ChoiceField as a representation to client
In [6]: PersonSerializerWithDRFChoiceField().to_representation(ann)                                                                                                
Out[6]: OrderedDict([('name', 'Ann'), ('sex', 2)])


# What returns NaturalChoiceField as a representation to client
In [7]: PersonSerializerNaturalChoiceField().to_representation(ann)                                                                                                
Out[7]: OrderedDict([('name', 'Ann'), ('sex', 'female')])


# Lets compare .to_internal_value() behaviour

# Native DRF ChoiceField conversion external choice value to internal raises exception
In [8]: new_bob_serializer = PersonSerializerWithDRFChoiceField(data={'name': 'NewBob', 'sex': 'male'})                                                            

In [9]: new_bob_serializer.is_valid(raise_exception=True)                                                                                                          
---------------------------------------------------------------------------
ValidationError                           Traceback (most recent call last)
<ipython-input-9-a86594992d60> in <module>
----> 1 new_bob_serializer.is_valid(raise_exception=True)

~/my_opensource/test_def_fields/venv/lib/python3.7/site-packages/rest_framework/serializers.py in is_valid(self, raise_exception)
    241 
    242         if self._errors and raise_exception:
--> 243             raise ValidationError(self.errors)
    244 
    245         return not bool(self._errors)

ValidationError: {'sex': [ErrorDetail(string='"male" is not a valid choice.', code='invalid_choice')]}


# Create serializer to check NaturalChoice behaviour from external representation
In [10]: new_bob_serializer = PersonSerializerNaturalChoiceField(data={'name': 'NewBob', 'sex': 'male'})                                                           


In [11]: new_bob_serializer.is_valid(raise_exception=True)                                                                                                         
Out[11]: True

# Everything is OK and external representation was successfully converted to internal DB representation
In [12]: new_bob_serializer.validated_data                                                                                                                         
Out[12]: OrderedDict([('name', 'NewBob'), ('sex', '1')])


```

So, as you can see native `ChoiceField` doesn't handle choices as it does django admin forms
by default, but `NaturalChoice` field can handle it.