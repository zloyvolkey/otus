from fields import Field, CharField, ArgumentsField, EmailField, BirthDayField, PhoneField, DateField, ClientIDsField, GenderField
from consts import ADMIN_LOGIN
from copy import deepcopy


class Request():
    def __init_subclass__(cls):
        super().__init_subclass__()

        declared_fields = []
        required_fields = []

        for attr_name, attr_value in cls.__dict__.items():
            if isinstance(attr_value, Field):
                attr_value.name = attr_name

                declared_fields.append(attr_name)

                if attr_value.required:
                    required_fields.append(attr_name)

        cls._declared_fields = declared_fields
        cls._required_fields = required_fields

    def __init__(self, body):
        self._errors = []
        self._initialized_fields = []

        body = deepcopy(body)

        for field_name, field_value in body.items():
            if field_name not in self._declared_fields:
                self._errors.append(f'undeclared field {field_name}')
                continue

            try:
                setattr(self, field_name, field_value)
            except Exception as e:
                self._errors.append(str(e))
                continue

            self._initialized_fields.append(field_name)

        missed = set(self._required_fields) - set(self._initialized_fields)
        if missed:
            self._errors.append(
                'missing required fields: "{}"'.format(', '.join(missed)))

    @property
    def errors(self):
        return self._errors

    @property
    def declared_fields(self):
        return self._declared_fields

    @property
    def required_fields(self):
        return self._required_fields

    @property
    def initialized_fields(self):
        return self._initialized_fields

    @property
    def is_valid(self):
        return len(self._errors) == 0


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, body):
        super(OnlineScoreRequest, self).__init__(body)

        valid = any(((self.first_name is not None and self.last_name is not None),
                     (self.email is not None and self.phone is not None),
                     (self.birthday is not None and self.gender is not None)))

        if not valid:
            self._errors.append('invalid arguments set')


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN
