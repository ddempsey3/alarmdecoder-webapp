# -*- coding: utf-8 -*-

from markupsafe import Markup 

from flask_wtf import FlaskForm as Form
from wtforms import (ValidationError, HiddenField, BooleanField, StringField,
        PasswordField, SubmitField)
from wtforms.validators import InputRequired, Length, EqualTo, Email
from wtforms.fields import EmailField

from ..user import User
from ..utils import (PASSWORD_LEN_MIN, PASSWORD_LEN_MAX,
        USERNAME_LEN_MIN, USERNAME_LEN_MAX)


class LoginForm(Form):
    next = HiddenField()
    login = StringField('Username or email', [InputRequired()])
    password = PasswordField('Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class SignupForm(Form):
    next = HiddenField()
    email = EmailField('Email', [InputRequired(), Email()],
            description="What's your email address?")
    password = PasswordField('Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description='%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    name = StringField('Choose your username', [InputRequired(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description="Don't worry. you can change it later.")
    agree = BooleanField('Agree to the ' +
        Markup('<a target="_blank" rel="noopener noreferrer" href="/terms">Terms of Service</a>'), [InputRequired()])
    submit = SubmitField('Sign up')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError('This username is taken')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is taken')


class RecoverPasswordForm(Form):
    email = EmailField('Your email', [Email()])
    submit = SubmitField('Send instructions')


class ChangePasswordForm(Form):
    activation_key = HiddenField()
    password = PasswordField('Password', [InputRequired()])
    password_again = PasswordField('Password again', [EqualTo('password', message="Passwords don't match")])
    submit = SubmitField('Save')


class ReauthForm(Form):
    next = HiddenField()
    password = PasswordField('Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)])
    submit = SubmitField('Reauthenticate')


class OpenIDForm(Form):
    openid = StringField('Your OpenID', [InputRequired()])
    submit = SubmitField('Log in with OpenID')


class CreateProfileForm(Form):
    openid = HiddenField()
    name = StringField('Choose your username', [InputRequired(), Length(USERNAME_LEN_MIN, USERNAME_LEN_MAX)],
            description="Don't worry. you can change it later.")
    email = EmailField('Email', [InputRequired(), Email()], description="What's your email address?")
    password = PasswordField('Password', [InputRequired(), Length(PASSWORD_LEN_MIN, PASSWORD_LEN_MAX)],
            description='%s characters or more! Be tricky.' % PASSWORD_LEN_MIN)
    submit = SubmitField('Create Profile')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first() is not None:
            raise ValidationError('This username is taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is not None:
            raise ValidationError('This email is taken.')

class LicenseAgreementForm(Form):
    agree = BooleanField('I agree to the license agreement', [InputRequired()], default=False)

    submit = SubmitField('Save')
