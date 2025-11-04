# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as Form
from wtforms import HiddenField, SubmitField, RadioField, DateField, StringField, PasswordField
from wtforms.validators import (InputRequired, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional)

from ..user import USER_ROLE, USER_STATUS, USER, ACTIVE
from ..utils import PASSWORD_LEN_MIN, PASSWORD_LEN_MAX

from ..widgets import ButtonField

class UserForm(Form):
    next = HiddenField()
    name = StringField('Username', [InputRequired()])
    email = StringField('Email', [InputRequired()])
    password = PasswordField('Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    password_again = PasswordField('Confirm Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX), EqualTo('password')])
    role_code = RadioField("Role", [AnyOf([str(val) for val in list(USER_ROLE.keys())])],
            choices=[(str(val), label) for val, label in list(USER_ROLE.items())], default=USER)
    status_code = RadioField("Status", [AnyOf([str(val) for val in list(USER_STATUS.keys())])],
            choices=[(str(val), label) for val, label in list(USER_STATUS.items())], default=ACTIVE)

    submit = SubmitField('Save')
    cancel = ButtonField('Cancel', onclick="location.href='/settings/users'")
