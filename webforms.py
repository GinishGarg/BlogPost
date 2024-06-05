from wtforms import StringField,SubmitField,EmailField,PasswordField,BooleanField,ValidationError,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from wtforms.widgets import TextArea
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from flask_ckeditor import CKEditorField

class SearchForm(FlaskForm):
     searched=StringField("search",validators=[DataRequired()])
     submit=SubmitField("submit")
     

class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField('Submit')


#create posts form
class PostForm(FlaskForm):
        title=StringField("Title",validators=[DataRequired()])
        content=CKEditorField("Content",validators=[DataRequired()])
        slug=StringField("Slug",validators=[DataRequired()])
        submit=SubmitField("Submit")

class Userform(FlaskForm):
    name=StringField("Name")
    submit=SubmitField("submit")
    
class passwordform(FlaskForm):
    email=EmailField("What's your email?")
    password_hash=PasswordField("What's your password?")
    submit=SubmitField("submit")
    

class Namerform(FlaskForm):
    name=StringField("Your Name", validators=[DataRequired()])
    username=StringField("UserName", validators=[DataRequired()])
    email=EmailField("Enter email",validators=[Email()])
    favorite_color=StringField("Favorite color")
    about_author=TextAreaField("About The Author")
    profile_pic=FileField("Profile Pic")
    password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
    password_hash2=PasswordField("Confirm Password",validators=[DataRequired()])
    submit=SubmitField("submit")

 # BooleanField
	# DateField
	# DateTimeField
	# DecimalField
	# FileField
	# HiddenField
	# MultipleField
	# FieldList
	# FloatField
	# FormField
	# IntegerField
	# PasswordField
	# RadioField
	# SelectField
	# SelectMultipleField
	# SubmitField
	# StringField
	# TextAreaField

	## Validators
	# DataRequired
	# Email
	# EqualTo
	# InputRequired
	# IPAddress
	# Length
	# MacAddress
	# NumberRange
	# Optional
	# Regexp
	# URL
	# UUID
	# AnyOf
	# NoneOf