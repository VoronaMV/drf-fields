# Django REST framework extra fields

## Project description
Serializer fields that don't exist in [Django REST framework](https://github.com/encode/django-rest-framework) but 
can be useful in some cases.

## Table of contents
- [Compatibility](#compatibility)
- [Installation](#installation)
- [Fields description](#fields-description)
  - [NaturalChoiceField](#fields-description)
    - [Compare with native DRF ChoiceField](#compare-representation-of-this-2-serializer-in-ipython-console)
  - [GetOrCreateSlugRelatedField](#getorcreateslugrelatedfield)
    - [Short demo in ipython console](#demo-of-getorcreateslugrelatedfield-in-ipython-console)
  - [TimestampField](#timestampfield)
    - [Short demo in ipython console](#demo-of-timestampfield-in-ipython-console)
  - [TimestampFromDateField](#timestampfromdatefield)
  
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
> `drf_fields.fields.NaturalChoiceField`

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
from drf_fields.fields import NaturalChoiceField
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

#### Compare representation of this 2 serializer in ipython console

Creating 2 person objects
```

In [1]: from myapp.models import Person                                                                                                                            

In [2]: from myapp.serializers import PersonSerializerNaturalChoiceField, PersonSerializerWithDRFChoiceField                                                       

In [3]: bob = Person.objects.create(name='Bob', sex=Person.MALE)                                                                                                   

In [4]: ann = Person.objects.create(name='Ann', sex=Person.FEMALE)                                                                                                 
```
Check that DB values really saved as numeric
```
In [5]: bob.sex, ann.sex                                                                                                                                           
Out[5]: (1, 2)
```
What returns native DRF `ChoiceField` as a representation to client
```
In [6]: PersonSerializerWithDRFChoiceField().to_representation(ann)                                                                                                
Out[6]: OrderedDict([('name', 'Ann'), ('sex', 2)])
````

What returns `NaturalChoiceField` as a representation to client
```
In [7]: PersonSerializerNaturalChoiceField().to_representation(ann)                                                                                                
Out[7]: OrderedDict([('name', 'Ann'), ('sex', 'female')])
```
Lets compare .to_internal_value() behaviour
Native DRF ChoiceField conversion external choice value to internal raises exception
```
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
```

Create serializer to check NaturalChoice behaviour from external representation
```
In [10]: new_bob_serializer = PersonSerializerNaturalChoiceField(data={'name': 'NewBob', 'sex': 'male'})                                                           

In [11]: new_bob_serializer.is_valid(raise_exception=True)                                                                                                         
Out[11]: True
```
Everything is OK and external representation was successfully converted to internal DB representation
```
In [12]: new_bob_serializer.validated_data                                                                                                                         
Out[12]: OrderedDict([('name', 'NewBob'), ('sex', '1')])
```

So, as you can see native `ChoiceField` doesn't handle choices as it does django admin forms
by default, but `NaturalChoice` field can handle it.

### GetOrCreateSlugRelatedField
> `drf_fields.fields.GetOrCreateSlugRelatedField`

A SlugRelatedField that make possible either to create relations
between objects that has already exists and which should be created.

Native DRF `SlugRelatedField` allow you to create new relation
between object has to be created and existed ones.
But sometime we want to created some object that has nested
field that represents one-to-one or one-to-many DB relationship 
to existed objects and new ones.

To be more clear imagine that we have Person and Skills that person 
can have. So it is represented by many-to-many relation.
So not to work with nested functionality it is easy to handle with 
`SlugRelatedField`, but when we retrieve request to create user it can 
looks like:
```json
{
    "name": "Bob",
     "skills": ["Python", "Java", "C#"]
}
```
And `Python` skill already exists in DB but `Java` and `C#` don't and
we want it to be created without overriding `.create()` of `PersonSerializer`.

So we have `models.py`
```python
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=200)


class Person(models.Model):

    name = models.CharField(max_length=255)
    skills = models.ManyToManyField(Skill, on_delete=models.CASCADE)
```

`serializers.py` have next content:
```python
from rest_framework import serializers
from drf_fields.fields import GetOrCreateSlugRelatedField
from myapp.models import Person


class PersonSerializer(serializers.ModelSerializer):
    skills = GetOrCreateSlugRelatedField(slug_field='name', get_or_craete=True)

    class Meta:
        model = Person
        fields = ('name', 'skills')
```

#### Demo of `GetOrCreateSlugRelatedField` in ipython console
```

```

### TimestampField
> `drf_fields.fields.TimestampField`

Field that allow simply works with timestamps in seconds with client side.
Originally you only can configure datetimes representation, but sometimes 
you need to set special field to retrieves and represents to client datetimes 
objects in timestamp format.

This field allow you to do it without any additional interaction.

So we have file `serializers.py`
```python
from rest_framework import serializers
from drf_fields.fields import TimestampField


class PersonSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    time = serializers.TimestampField()
```

#### Demo of `TimestampField` in ipython console
```

```

### TimestampFromDateField
> `drf_fields.fields.TimestampFromDateField`

The same field as `TimestampField` but for date representation.

### RecursiveField
> `drf_fields.fields.RecursiveField`

Field for recursive tree scaling with set depth.

Sometimes you can have tree database table structure. 
The simples case, when you  have `self related` one-to-many 
relation in table. When you have this case - you may want to represent 
this structure as a tree at the client side (for example: organization structure 
of company).

