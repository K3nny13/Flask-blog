from flask import render_template, url_for, flash, redirect, request
from flask_blog import app, db, bcrypt
from flask_blog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flask_blog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


posts = [{
    'author': 'Kenny',
    'title': 'First Blog',
    'content': 'This is a First Blog Post',
    'date': '14 December 2018' 
},
{
    'author': 'Kenny',
    'title': 'First Blog',
    'content': 'This is a First Blog Post',
    'date': '14 December 2018' 
}]

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', posts=posts, title='Index')

@app.route('/about')
def about():
    return render_template('about.html', title='About')
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Account created, you may now login below', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash('You have been logged in', 'success')
			return redirect(next_page) if next_page else redirect(url_for('index'))
		else:
			flash('Login failed', 'danger')
	return render_template('login.html', title='Login', form=form)
	
@app.route('/logout')
def logout():
	logout_user()
	flash('You have successfully logged out', 'success')
	return redirect(url_for('index'))
	
@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	profile_image = url_for('static', filename=f'profile_pics/{current_user.image_file}')
	return render_template('account.html', title='Account', profile_image=profile_image, form=form)
		