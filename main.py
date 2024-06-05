from flask import Flask,render_template,flash,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime ,date
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,UserMixin,LoginManager,login_required,logout_user,current_user
from webforms import Namerform ,passwordform , LoginForm , PostForm,SearchForm
from flask_ckeditor import CKEditor
from werkzeug.utils import secure_filename
import uuid as uuid
import os


app=Flask(__name__)
ckeditor=CKEditor(app)
app.config['SECRET_KEY']="My secret super key"


# app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://postgres:test@localhost:5432/Users"

db=SQLAlchemy(app)
migrate=Migrate(app,db)

UPLOAD_FOLDER='static/images/'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER



@app.route('/adminster')
@login_required
def admin():
    id=current_user.id
    if id==8:
        return render_template('administer.html')
    else:
        flash('Sorry! you must be an Admin to access this page...') 
        return redirect(url_for('dashboard'))       
    

# Add posts
@app.route("/add-post",methods=['GET',"POST"])
# @login_required
def add_post():
    form=PostForm()

    if form.validate_on_submit():
        poster= current_user.id
        post=Posts(title=form.title.data,content=form.content.data,poster_id=poster,slug=form.slug.data)

        #clear the form
        form.title.data=''
        form.content.data=''
        form.slug.data=''

        db.session.add(post)
        db.session.commit()
        flash("Submitted succesfully!")
    return render_template("add_post.html",form=form)


@app.route("/delete/<int:id>")
@login_required
def delete_user(id):
    if id==current_user.id or id==8:
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
    else:
        flash('You don\'t have the permission to delete this user')
        return redirect(url_for('dashboard'))
@app.route('/posts/delete/<int:id>')
def delete_post(id):
    post_to_delete=Posts.query.get_or_404(id)
    id=current_user.id
    if id==post_to_delete.poster_id or id==8:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash('Post deleted successfully!')

            posts=Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html",posts=posts)
        except:
            flash('there was a problem deleting the post')
            return render_template("posts.html",posts=posts)
    else:
        flash("You cannot delete this post")
        posts=Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html',posts=posts)
    

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route("/date")
def get_current_date():
    favorite_pizza={"John": "pepproni","Mary":"Cheese",'Tim':"Mushroom"}
    return favorite_pizza
    # return {"Date": date.today()}

@app.route("/")
def home():
    return render_template('homepage.html')

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



#Create login page
@app.route('/login',methods=["POST","GET"])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash('Login Successfull!!','success')
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password Try Again",'error')   
        else:
            flash("That user does not exist",'error')         
            
    return render_template('login.html',form=form)

@app.route('/dashboard',methods=["POST","GET"])
@login_required
def dashboard():
    form = Namerform()
    id=current_user.id  
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        name_to_update.profile_pic = request.files['profile_pic']
        if request.files['profile_pic']:

            pic_filename=secure_filename(name_to_update.profile_pic.filename)
            pic_name=str(uuid.uuid1()) + "_" + pic_filename
        
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER']),pic_name)
            
            name_to_update.profile_pic=pic_name
            try:
                db.session.commit()
                flash("User updated successfully.")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
            except:
                flash("Error! Try again later...")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update,id=id)
        else:
            db.session.commit()
            flash("User updated successfully.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update,id=id)
    
#create a blog post model
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
        post.slug=form.slug.data
        post.content=form.content.data
        #update database
        db.session.add(post)
        db.session.commit()
        flash('Post has beeen Updated!')
        return redirect(url_for('post',id=post.id))
    if current_user.id==post.poster_id or id==8:
        form.title.data=post.title
        form.slug.data=post.slug
        form.content.data=post.content
        return render_template('edit_post.html',form=form)
    else:
        flash('You are not Authorized to Edit this page')
        posts=Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html',posts=posts)
    
@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

@app.route('/search',methods=["POST"])
def search():
    form=SearchForm()
    posts=Posts.query
    if form.validate_on_submit():
        post.searched=form.searched.data
        posts=posts.filter(Posts.content.like('%'+post.searched+'%'))
        posts=posts.order_by(Posts.title).all()
        return render_template('search.html',form=form,searched=post.searched,posts=posts)
    



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



           


   
    

with app.app_context():
    db.create_all()

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
    



@app.route("/update/<int:id>", methods=["POST", "GET"])
@login_required
def update(id):
    form = Namerform()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST" and id==current_user.id:
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        name_to_update.username = request.form['username']
        name_to_update.about_author=request.form['about_author']
       
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            pic_filename=secure_filename(name_to_update.profile_pic.filename)
            pic_name=str(uuid.uuid1()) + "_" + pic_filename
        
            name_to_update.profile_pic.save(os.path.join(app.config['UPLOAD_FOLDER'],pic_name))
            
            name_to_update.profile_pic=pic_name
            try:
                db.session.commit()
                flash("User updated successfully.")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update)
            except:
                flash("Error! Try again later...")
                return render_template("dashboard.html", form=form, name_to_update=name_to_update,id=id)
        else:
            db.session.commit()
            flash("User updated successfully.")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update,id=id)
    
				
class Users(db.Model,UserMixin):
    _table_="signup"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),nullable=False,unique=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(150),nullable=False,unique=True)
    favorite_color=db.Column(db.String(100))
    profile_pic=db.Column(db.String(),nullable=True)
    about_author=db.Column(db.Text)
    date_added=db.Column(db.DateTime, default=datetime.utcnow,nullable=False)
    password_hash=db.Column(db.String(1020))
    #User can have many posts
    posts= db.relationship('Posts',backref="poster")


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

class Posts(db.Model):
    id= db.Column(db.Integer(),primary_key=True)
    title=db.Column(db.String(255))
    content=db.Column(db.Text)
    #author=db.Column(db.String(255))
    date_posted=db.Column(db.DateTime,default=datetime.utcnow)
    slug=db.Column(db.String(255))
    #Foreign key to link users(refer to primary key)
    poster_id= db.Column(db.Integer, db.ForeignKey('users.id'))

        



app.run(debug=True)