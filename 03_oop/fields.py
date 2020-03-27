# -*- coding: utf-8 -*-

import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from consts import UNKNOWN, GENDERS


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

        email_pattern = r'.+@.+\..+'

        if not re.match(email_pattern, str(value)):
            raise ValueError(f'invalid email address: {value}')


class PhoneField(Field):
    def __init__(self, required=False, nullable=True):
        super(PhoneField, self).__init__(
            type=(int, str), required=required, nullable=nullable)

    def validate(self, value):
        super(PhoneField, self).validate(value)

        phone_pattern = r'^7\d{10}$'
        if not re.match(phone_pattern, str(value)):
            raise ValueError(f'invalid phone number: {value}')


class DateField(Field):
    def __init__(self, required=False, nullable=True):
        super(DateField, self).__init__(type=str,
                                        required=required, nullable=nullable)

    def validate(self, value):
        super(DateField, self).validate(value)

        if value:
            try:
                datetime.strptime(value, '%d.%m.%Y')
            except ValueError:
                raise ValueError(f'invalid date format: {value}')


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
                    raise ValueError
            except ValueError:
                raise ValueError(f'invalid date format: {value}')


class GenderField(Field):
    def __init__(self, required=False, nullable=True):
        super(GenderField, self).__init__(
            type=int, required=required, nullable=nullable)

    def validate(self, value):
        if not isinstance(value, self.type):
            raise Exception('invalid value type of field "gender"')

        if not value and value != UNKNOWN and not self.nullable:
            Exception('field "gender" cannot be empty')

        if value not in GENDERS:
            raise Exception('invalid value of field "gender"')


class ClientIDsField(Field):
    def __init__(self, required=True, nullable=False):
        super(ClientIDsField, self).__init__(
            type=(list, tuple), required=required, nullable=nullable)

    def validate(self, value):
        super(ClientIDsField, self).validate(value)

        if value:
            for obj in value:
                if not isinstance(obj, int) or obj < 0:
                    raise Exception(f'invalid client id {value}')
