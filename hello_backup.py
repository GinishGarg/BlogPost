from flask import Flask,render_template,flash,request,redirect,url_for
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,EmailField,PasswordField,BooleanField,ValidationError
from wtforms.validators import DataRequired,Email,EqualTo,Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime ,date
from werkzeug.security import generate_password_hash,check_password_hash
from wtforms.widgets import TextArea
from flask_login import login_user,UserMixin,LoginManager,login_required,logout_user,current_user
app=Flask(__name__)
app.config['SECRET_KEY']="My secret super key"
# app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://postgres:test@localhost:5432/Users"

db=SQLAlchemy(app)
migrate=Migrate(app,db)


#Create logout page
@app.route("/logout",methods=['POST','GET'])
@login_required
def logout():
    logout_user()
    flash("You have been logout")
    return redirect(url_for('login'))


#Flask login stuff
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class LoginForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField('Submit')
#Create login page
@app.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash('Login Successfull!!')
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password Try Again")   
        else:
            flash("That user does not exist")         
            
    return render_template('login.html',form=form)

@app.route('/dashboard',methods=["POST","GET"])
@login_required
def dashboard():
    form=LoginForm()
    return render_template('dashboard.html',form=form)
#create a blog post model
class Posts(db.Model):
    id= db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text)
    author=db.Column(db.String(255))
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)
    slug=db.Column(db.String(255))

#create posts form
class PostForm(FlaskForm):
        title=StringField("Title",validators=[DataRequired()])
        content=StringField("Content",validators=[DataRequired()], widget=TextArea())
        author=StringField("Author",validators=[DataRequired()])
        slug=StringField("Slug",validators=[DataRequired()])
        submit=SubmitField("Submit")

# create show blog page
@app.route('/posts')
def posts():

    posts=Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",posts=posts)

@app.route("/posts/<int:id>")
def post(id):
    post=Posts.query.get_or_404(id)
    return render_template('post.html',post=post)
@app.route('/posts/edit/<int:id>',methods=['POST','GET'])
@login_required
def edit_post(id):
    post=Posts.query.get_or_404(id)
    form=PostForm()
    if form.validate_on_submit():
        post.title=form.title.data
        post.author=form.author.data
        post.slug=form.slug.data
        post.content=form.content.data
        #update database
        db.session.add(post)
        db.session.commit()
        flash('Post has beeen Updated!')
        return redirect(url_for('post',id=post.id))
    form.title.data=post.title
    form.author.data=post.author
    form.slug.data=post.slug
    form.content.data=post.content
    return render_template('edit_post.html',form=form)
# Add posts
@app.route("/add-post",methods=['GET',"POST"])
# @login_required
def add_post():
    form=PostForm()

    if form.validate_on_submit():
        post=Posts(title=form.title.data,content=form.content.data,author=form.author.data,slug=form.slug.data)

        #clear the form
        form.title.data=''
        form.content.data=''
        form.author.data=''
        form.slug.data=''

        db.session.add(post)
        db.session.commit()
        flash("Submitted succesfully!")
    return render_template("add_post.html",form=form)

@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete=Posts.query.get_or_404(id)
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted successfully!')

        posts=Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html",posts=posts)
    except:
        flash('there was a problem deleting the post')
        return render_template("posts.html")


           

class Users(db.Model,UserMixin):
    _table_="signup"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=True)
    favorite_color=db.Column(db.String(100))
    date_added=db.Column(db.DateTime, default=datetime.utcnow,nullable=False)
    password_hash=db.Column(db.String(1020))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)
    

with app.app_context():
    db.create_all()
    
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
    password_hash=PasswordField("Password",validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
    password_hash2=PasswordField("Confirm Password",validators=[DataRequired()])
    submit=SubmitField("submit")


@app.route("/update/<int:id>", methods=["POST", "GET"])
def update(id):
    form = Namerform()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User updated successfully.")
            return render_template("update.html", form=form, name_to_update=name_to_update)
        except:
            flash("Error! Try again later...")
            return render_template("update.html", form=form, name_to_update=name_to_update,id=id)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update,id=id)
				
@app.route("/date")
def get_current_date():
    favorite_pizza={"John": "pepproni","Mary":"Cheese",'Tim':"Mushroom"}
    return favorite_pizza
    # return {"Date": date.today()}

        
@app.route("/delete/<int:id>")
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    email = None
    form = Namerform()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('signup.html', name=name, email=email, form=form, our_users=our_users)

    except:
        flash("There was a problem deleting the user")
        return render_template('signup.html', name=name, email=email, form=form, our_users=our_users)


@app.route("/")
def home():
    return render_template('homepage.html')
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route("/test_pw",methods=["POST","GET"])
def test_pw():
    email=None
    password=None
    pw_to_check=None
    passed=None
    form=passwordform()
    if form.validate_on_submit():
        email=form.email.data
        password=form.password_hash.data

        form.email.data=''
        form.password_hash.data=''

        pw_to_check=Users.query.filter_by(email=email).first()
        passed=check_password_hash(pw_to_check.password_hash,password)
        
        flash("signed in successfully")    

    return render_template('test_pw.html',passed=passed,pw_to_check=pw_to_check,email=email,password=password,form=form)

@app.route("/signup",methods=["POST","GET"])
def signup():
    name=None
    email=None
    form=Namerform()
    if form.validate_on_submit():
        User=Users.query.filter_by(email=form.email.data).first()
        
        
        if User is None:
            hashed_pw=generate_password_hash(form.password_hash.data)
            User=Users(username=form.username.data,name=form.name.data,email=form.email.data,favorite_color=form.favorite_color.data,password_hash=hashed_pw)
            db.session.add(User)
            db.session.commit()
        name=form.name.data
        form.name.data=''
        form.username.data=''
        form.email.data=''
        form.favorite_color.data=''
        form.password_hash.data=''
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