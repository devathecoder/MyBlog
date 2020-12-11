from flask import Flask, render_template, request, session, redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
from flask_mail import Mail
from datetime import datetime
import os
import math

# Repository used is MyBlog

with open("config.json", "r") as c:
    params = json.load(c)["params"]
local_server = True


users = []
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_pass']
)
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)


class Contact(db.Model):
    '''
    sno, name, email, phone_num, mes, date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=False, nullable=False)
    phone_num = db.Column(db.String(80), unique=False, nullable=False)
    msg = db.Column(db.String(80), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable = False)

class Post(db.Model):
    '''
    sno, name, email, phone_num, mes, date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(20), unique=False, nullable=False)
    content = db.Column(db.String(120), unique=False, nullable=False)
    tagline = db.Column(db.String(120), unique=False, nullable=False)
    img_file = db.Column(db.String(12), nullable = False)
    date = db.Column(db.String(12), unique=False, nullable = False)

class Usersignup(db.Model):
    '''
    sno, name, email, phone_num, mes, date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(20), unique=False, nullable=False)
    password = db.Column(db.String(50), unique = False, nullable = False)
    date = db.Column(db.String(12), unique=False, nullable=False)

class Video(db.Model):
    '''
    sno, name, email, phone_num, mes, date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    tagline = db.Column(db.String(120), unique=False, nullable=False)
    slug = db.Column(db.String(20), unique=False, nullable=False)
    link = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(12), unique=False, nullable = False)

class University(db.Model):
    '''
    sno, name, email, phone_num, mes, date
    '''
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(20), unique=False, nullable=False)
    content = db.Column(db.String(120), unique=False, nullable=False)
    tagline = db.Column(db.String(120), unique=False, nullable=False)
    img_file = db.Column(db.String(12), nullable = False)
    date = db.Column(db.String(12), unique=False, nullable = False)



@app.route("/", methods = ['GET', 'POST'])
def home():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    # [0:params['no_of_posts']]
    page = request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[(page - 1)*int(params['no_of_posts']) : (page - 1)*int(params['no_of_posts']) + int(params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"
    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)

    # if request.method == 'POST':
    #     session.pop('user_id', None)
    #     username = request.form['username']
    #     password = request.form['password']
    #
    #     user = [x for x in users if x.username == username][0]
    #     if user and user.password == password:
    #         session['user_id'] = user.id
    #         return redirect('/success')
    #     return redirect('/')
    return render_template('index.html', params = params, posts = posts, prev = prev,  next = next)


@app.route("/about")
def about():
    return render_template('about.html', params = params)


@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
    users = Usersignup.query.filter_by().all()
    video = Video.query.filter_by().all()
    university = University.query.filter_by().all()
    if 'user' in session and session['user'] == params['admin_user']:
        posts = Post.query.all()
        return render_template('dashboard.html', params = params, posts = posts)
    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            #set the session variable
            session['user'] = username
            posts = Post.query.all()
            video = Video.query.filter_by().all()
            university = University.query.filter_by().all()
            return render_template('dashboard.html', params=params, posts = posts, users = users, video= video, details = university)
    return render_template('login.html', params = params, users = users, video = video, details = university)


@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params = params, post = post)

@app.route("/details/<string:university_slug>", methods = ['GET'])
def university_route(university_slug):
    university = University.query.filter_by(slug = university_slug).first()
    return render_template('details.html', params = params, details = university)

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        msg = request.form.get('msg')

        entry = Contact(name = name, email = email, phone_num = phone, msg = msg, date = datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New message from " +  name, sender = email, recipients = [params['gmail_user']], body = msg + "\n" + phone)

    return render_template('contact.html', params = params)

@app.route("/edit-post/<string:sno>", methods=['GET', 'POST'])
def editpost(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('Content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Post(title=box_title, tagline=tline, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit-post/' + sno)
        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit-post.html', params=params, post=post, sno=sno)

@app.route("/edit-university/<string:sno>", methods=['GET', 'POST'])
def edituniversity(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('Content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                university = University(title=box_title, tagline=tline, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(university)
                db.session.commit()
            else:
                university = University.query.filter_by(sno=sno).first()
                university.title = box_title
                university.slug = slug
                university.content = content
                university.tagline = tline
                university.img_file = img_file
                university.date = date
                db.session.commit()
                return redirect('/edit-university/' + sno)
        university = University.query.filter_by(sno=sno).first()
        return render_template('edit-university.html', params=params, details=university, sno=sno)


@app.route("/delete-post/<string:sno>", methods=['GET', 'POST'])
def deletepost(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Post.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

@app.route("/edit-video/<string:sno>", methods=['GET', 'POST'])
def editvideo(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            link = request.form.get('Content')
            date = datetime.now()

            if sno == '0':
                video = Video(title=box_title, tagline=tline, slug=slug, link = link, date=date)
                db.session.add(video)
                db.session.commit()
            else:
                video = Video.query.filter_by(sno=sno).first()
                video.title = box_title
                video.tagline = tline
                video.slug = slug
                video.link = link
                video.date = date
                db.session.commit()
                return redirect('/edit-video/' + sno)
        video = Video.query.filter_by(sno=sno).first()
        return render_template('edit-video.html', params=params, video = video, sno=sno)

@app.route("/delete-video/<string:sno>", methods=['GET', 'POST'])
def deletevideo(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        video = Video.query.filter_by(sno=sno).first()
        db.session.delete(video)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/signup", methods= ['GET', 'POST'])
def usersignup():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        date = datetime.now()

        entry = Usersignup(username = name, email = email, password = password, date = date)
        db.session.add(entry)
        db.session.commit()
        mail.send_message("New User Signed Up " + name, sender=email, recipients=[params['gmail_user']], body = "The username is : " + name + "\n" + "Email id is : " + email + "\n" + "At : " + str(date))
    return render_template('usersignup.html', params = params)

@app.route("/login", methods= ['GET', 'POST'])
def userlogin():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('username')
        password = request.form.get('password')
        users = Usersignup.query.filter_by().all()  # Access a database table Very Important *************************************
        for x in users:
            if x.username == name and x.password == password:
                params['login'] = True
                params['usernow'] = name
                params['error'] = False
                return redirect('/')
        params['error'] = True
        return redirect('/')

@app.route("/logoutuser")
def logoutuser():
    # session.pop('user')
    params['login'] = False
    params['usernow'] = None
    params['error'] = 'abc'
    return redirect('/')

@app.route("/videos", methods= ['GET', 'POST'])
def Videogrid():
    video = Video.query.filter_by().all()
    return render_template("videogrid.html", params= params, video = video)


@app.route("/video/<string:sno>", methods = ['GET', 'POST'])
def video(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('Content')
            date = datetime.now()

            if sno == '0':
                video = Video(title = box_title, tagline = tline, slug = slug, link = content, date = date)
                db.session.add(video)
                db.session.commit()
            else:
                video = Video.query.filter_by(sno = sno).first()
                video.title = box_title
                video.slug = slug
                video.content = content
                video.tagline = tline
                video.date = date
                db.session.commit()
                return redirect('/video/' + sno)
        video = Video.query.filter_by(sno = sno).first()
        return render_template('video.html', params = params, video = video, sno= sno)
    else:
        video = Video.query.filter_by(sno = sno).first()
        return render_template('videolayout.html', play = video.link, params= params)



if __name__ == '__main__':
    app.run(debug=True)