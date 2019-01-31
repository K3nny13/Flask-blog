from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import db, bcrypt
from flask_blog.models import User, Post
from flask_blog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flask_blog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users .route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Account created, you may now login below', 'success')
		return redirect(url_for('users.login'))
	return render_template('register.html', title='Register', form=form)
	
@users .route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			flash('You have been logged in', 'success')
			return redirect(next_page) if next_page else redirect(url_for('main.index'))
		else:
			flash('Login failed', 'danger')
	return render_template('login.html', title='Login', form=form)
	
@users .route('/logout')
def logout():
	logout_user()
	flash('You have successfully logged out', 'success')
	return redirect(url_for('main.index'))
	
@users .route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated', 'success')
		return redirect(url_for('users.account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	profile_image = url_for('static', filename=f'profile_pics/{current_user.image_file}')
	return render_template('account.html', title='Account', profile_image=profile_image, form=form)
	
@users .route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=2)
	title = username + "'s Posts"
	return render_template('user_posts.html', posts=posts, user=user, title=title)
	
@users .route('/reset_password', methods=['GET', 'POST'])
def reset_password():
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset password', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_request.html', form=form, title='Reset Password')

@users .route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.index'))
	user = User.verify_reset_token(token)
	if not user:
		flash('That is an invalid token', 'warning')
		return redirect(url_for('users.reset_password'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password was updated! You may now login below', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_token.html', form=form, title='Reset Password')