from flask import Flask,render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,EmailField
from wtforms.validators import DataRequired,Email
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime 

app=Flask(__name__)
app.config['SECRET_KEY']="My secret super key"
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://postgres:test@localhost:5432/Users"

db=SQLAlchemy(app)
migrate=Migrate(app,db)



class Users(db.Model):
    _table_="signup"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=True)
    favorite_color=db.Column(db.String(100))
    date_added=db.Column(db.DateTime, default=datetime.utcnow,nullable=False)
    

with app.app_context():
    db.create_all()
    
# class Userform(FlaskForm):
#     name=StringField("Name",Validators=[DataRequired()])
#     email=EmailField("Email",validators=[Email()])
#     submit=SubmitField("submit")
    

class Namerform(FlaskForm):
    name=StringField("Your Name", validators=[DataRequired()])
    email=EmailField("Enter email",validators=[Email()])
    favorite_color=StringField("Favorite color")
    submit=SubmitField("submit")


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    form = Namerform()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User updated successfully.")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error! Try again later...")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update)
				
        
        
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

@app.route("/signup",methods=["POST","GET"])
def signup():
    name=None
    email=None
    form=Namerform()
    if form.validate_on_submit():
        User=Users.query.filter_by(email=form.email.data).first()
        
        
        if User is None:
            User=Users(name=form.name.data,email=form.email.data,favorite_color=form.favorite_color.data)
            db.session.add(User)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.email.data=''
        form.favorite_color.data=''
        flash("Signed up successfully.")
        
    our_users=Users.query.order_by(Users.date_added)
        
		
    return render_template('signup.html',name=name,email=email,form=form,our_users=our_users)



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