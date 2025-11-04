# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm as Form
from wtforms import (ValidationError, HiddenField, StringField, HiddenField,
        PasswordField, SubmitField, TextAreaField, IntegerField, RadioField,
        FileField, DecimalField, BooleanField, SelectField, FormField, FieldList)
from wtforms.validators import (InputRequired, Length, EqualTo, Email, NumberRange,
        URL, AnyOf, Optional, Regexp)

from ..widgets import ButtonField

class UpdateFirmwareForm(Form):
    firmware_file = FileField('Firmware File', [InputRequired()])

    submit = SubmitField('Upload')
    cancel = ButtonField('Cancel', onclick="location.href='/settings'")

class UpdateFirmwareJSONForm(Form):
    firmware_file_json = SelectField('Firmware File', coerce=str)

    json_submit = SubmitField('Upload')
    cancel = ButtonField('Cancel', onclick="location.href='/settings'")
