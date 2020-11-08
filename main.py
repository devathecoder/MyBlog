from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
from flask_mail import Mail
from datetime import datetime
import os
import math


with open("config.json", "r") as c:
    params = json.load(c)["params"]
local_server = True

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


@app.route("/")
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
    return render_template('index.html', params = params, posts = posts, prev = prev,  next = next)


@app.route("/about")
def about():
    return render_template('about.html', params = params)


@app.route("/dashboard", methods = ['GET', 'POST'])
def dashboard():
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
            return render_template('dashboard.html', params=params, posts = posts)
    return render_template('login.html', params = params)


@app.route("/post/<string:post_slug>", methods = ['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug = post_slug).first()
    return render_template('post.html', params = params, post = post)


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

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('Content')
            img_file = request.form.get('img_file')
            date = datetime.now()

            if sno == '0':
                post = Post(title = box_title, tagline = tline, slug = slug, content = content, img_file = img_file, date = date)
                db.session.add(post)
                db.session.commit()
            else:
                post = Post.query.filter_by(sno = sno).first()
                post.title = box_title
                post.slug = slug
                post.content = content
                post.tagline = tline
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/' + sno)
        post = Post.query.filter_by(sno = sno).first()
        return render_template('edit.html', params = params, post = post, sno= sno)

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

@app.route("/delete/<string:sno>", methods = ['GET', 'POST'])
def delete(sno):
    if 'user' in session and session['user'] == params['admin_user']:
        post = Post.query.filter_by(sno = sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)