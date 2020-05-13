# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

from exceptions import ValidationError
from consts import UNKNOWN, GENDERS, EMAIL_PATTERN, PHONE_PATTERN, DATE_FORMAT


class Field(object):

    def __init__(self, type, nullable=False, required=False):
        self.name = None
        self.type = type
        self.required = required
        self.nullable = nullable

    def __set__(self, instance, value):
        self.validate(value)
        instance.__dict__[self.name] = value

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def validate(self, value):
        if not (value or self.nullable):
            raise Exception(f'field {self.name} cannot be empty')

        if not isinstance(value, self.type):
            raise Exception(f'field {self.name}, invalid type {self.type}')


class CharField(Field):
    def __init__(self, required=False, nullable=True):
        super(CharField, self).__init__(
            type=str, required=required, nullable=nullable)


class ArgumentsField(Field):
    def __init__(self, required=False, nullable=True):
        super(ArgumentsField, self).__init__(
            type=dict, required=required, nullable=nullable)


class EmailField(CharField):
    def __init__(self, required=False, nullable=True):
        super(EmailField, self).__init__(required=required, nullable=nullable)

    def validate(self, value):
        super(EmailField, self).validate(value)

        if not re.match(EMAIL_PATTERN, str(value)):
            raise ValidationError(f'invalid email address: {value}')


class PhoneField(Field):
    def __init__(self, required=False, nullable=True):
        super(PhoneField, self).__init__(
            type=(int, str), required=required, nullable=nullable)

    def validate(self, value):
        super(PhoneField, self).validate(value)

        if not re.match(PHONE_PATTERN, str(value)):
            raise ValidationError(f'invalid phone number: {value}')


class DateField(Field):
    def __init__(self, required=False, nullable=True):
        super(DateField, self).__init__(type=str,
                                        required=required, nullable=nullable)

    def validate(self, value):
        super(DateField, self).validate(value)

        if value:
            try:
                datetime.strptime(value, DATE_FORMAT)
            except ValueError:
                raise ValidationError(f'invalid date format: {value}')


class BirthDayField(DateField):
    def __init__(self, required=False, nullable=True):
        super(BirthDayField, self).__init__(
            required=required, nullable=nullable)

    def validate(self, value):
        super(BirthDayField, self).validate(value)

        if value:
            try:
                value = datetime.strptime(value, '%d.%m.%Y').date()
                from_date = datetime.now()
                from_date -= relativedelta(years=70)
                if value.year < from_date.year:
                    raise ValidationError
            except ValueError:
                raise ValidationError(f'invalid date format: {value}')


class GenderField(Field):
    def __init__(self, required=False, nullable=True):
        super(GenderField, self).__init__(
            type=int, required=required, nullable=nullable)

    def validate(self, value):
        if not isinstance(value, self.type):
            raise ValidationError('invalid value type of field "gender"')

        if not value and value != UNKNOWN and not self.nullable:
            raise ValidationError('field "gender" cannot be empty')

        if value not in GENDERS:
            raise ValidationError('invalid value of field "gender"')


class ClientIDsField(Field):
    def __init__(self, required=True, nullable=False):
        super(ClientIDsField, self).__init__(
            type=(list, tuple), required=required, nullable=nullable)

    def validate(self, value):
        super(ClientIDsField, self).validate(value)

        if value:
            for obj in value:
                if not isinstance(obj, int) or obj < 0:
                    raise ValidationError(f'invalid client id {value}')
