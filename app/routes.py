from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app
from app.models import User, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, CreateListingForm, EditListingForm
from datetime import datetime
from app.models import Listing

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    listings = Listing.query.filter_by(is_complete=False).order_by(Listing.timestamp.desc()).paginate(page, app.config['LISTINGS_PER_PAGE'], False) #TODO: need a better query to filter out filled/complete projects and sort by tag
    next_url = url_for('index', page=listings.next_num) \
        if listings.has_next else None
    prev_url = url_for('index', page=listings.prev_num) \
        if listings.has_prev else None
    return render_template('index.html', title='Home', listings=listings.items, next_url=next_url, prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, major=form.major.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Welcome, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    listings = user.listings.order_by(Listing.timestamp.desc()).paginate(page, app.config['LISTINGS_PER_PAGE'], False)
    next_url = url_for('user', username=user.username, page=listings.next_num) \
        if listings.has_next else None
    prev_url = url_for('user', username=user.username, page=listings.prev_num) \
        if listings.has_prev else None
    return render_template('user.html', user=user, listings=listings.items, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/create_listing', methods=['GET', 'POST'])
@login_required
def create_listing():
    form = CreateListingForm()
    if form.validate_on_submit():
        listing = Listing(title=form.title.data, body=form.body.data, desired_size=form.desired_size.data, owner=current_user)
        db.session.add(listing)
        db.session.commit()
        flash('Your listing is now posted!')
        return redirect(url_for('index'))
    return render_template('create_listing.html', title='Create a Listing', form=form)

@app.route('/view_listing/<listing_id>', methods=['GET', 'POST'])
@login_required
def view_listing(listing_id):
    form = EditListingForm()
    listing = Listing.query.filter_by(id=listing_id).first_or_404()
    if listing.is_complete == True:
        del form.complete_project
    if form.validate_on_submit():
        if not listing.is_complete and form.complete_project.data:
            #Listing.query.filter_by(id=listing_id).first_or_404().update({"is_complete"}: (True))
            setattr(listing, 'is_complete', True)
            db.session.commit()
        if form.delete_project.data:
            Listing.query.filter_by(id=listing_id).delete()
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('view_listing.html', listing=listing, form=form)