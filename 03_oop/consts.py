# -*- coding: utf-8 -*-

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"

UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

EMAIL_PATTERN = r'.+@.+\..+'
PHONE_PATTERN = r'^7\d{10}$'

DATE_FORMAT = '%d.%m.%Y'
