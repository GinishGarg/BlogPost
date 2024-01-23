from flask import Flask,render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,EmailField
from wtforms.validators import DataRequired,Email


app=Flask(__name__)
app.config['SECRET_KEY']="My secret super key"

class Namerform(FlaskForm):
    name=StringField("Your Name", validators=[DataRequired()])
    email=EmailField("Enter email",validators=[Email()])
    submit=SubmitField("submit")



@app.route("/")
def home():
    return render_template('homepage.html')
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route("/signin",methods=["POST","GET"])
def signin():
    name=None
    email=None
    form=Namerform()
    if form.validate_on_submit():
        name=form.name.data
        form.name.data=''
        email=form.email.data
        form.email.data=''    
        flash("signed in successfully")    

    return render_template('signin.html',name=name,email=email,form=form)





app.run(debug=True)
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