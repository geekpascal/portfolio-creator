from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    sections = db.relationship('Section', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Forms
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class SectionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Submit')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    features = [
        {'icon': 'star', 'title': 'Professional Templates', 'description': 'Choose from a variety of sleek, modern templates designed to showcase your work.'},
        {'icon': 'users', 'title': 'Easy Collaboration', 'description': 'Share your portfolio and get feedback from peers and potential employers.'},
        {'icon': 'briefcase', 'title': 'Career Advancement', 'description': 'Increase your visibility and attract better job opportunities with a standout portfolio.'}
    ]
    testimonials = [
        {'name': 'Alex Johnson', 'role': 'UX Designer', 'quote': 'PortfolioCreator helped me land my dream job. The templates are stunning and so easy to customize!'},
        {'name': 'Samantha Lee', 'role': 'Freelance Developer', 'quote': 'As a freelancer, having a professional portfolio is crucial. This platform made it incredibly simple to showcase my projects.'}
    ]
    return render_template('home.html', features=features, testimonials=testimonials)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    sections = Section.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', title='Dashboard', sections=sections)

@app.route('/add_section', methods=['GET', 'POST'])
@login_required
def add_section():
    form = SectionForm()
    if form.validate_on_submit():
        section = Section(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(section)
        db.session.commit()
        flash('Your section has been created!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_section.html', title='Add Section', form=form)

@app.route('/edit_section/<int:section_id>', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    section = Section.query.get_or_404(section_id)
    if section.author != current_user:
        abort(403)
    form = SectionForm()
    if form.validate_on_submit():
        section.title = form.title.data
        section.content = form.content.data
        db.session.commit()
        flash('Your section has been updated!', 'success')
        return redirect(url_for('dashboard'))
    elif request.method == 'GET':
        form.title.data = section.title
        form.content.data = section.content
    return render_template('edit_section.html', title='Edit Section', form=form, section=section)

@app.route('/delete_section/<int:section_id>', methods=['POST'])
@login_required
def delete_section(section_id):
    section = Section.query.get_or_404(section_id)
    if section.author != current_user:
        abort(403)
    db.session.delete(section)
    db.session.commit()
    flash('Your section has been deleted!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/view_portfolio')
@login_required
def view_portfolio():
    sections = Section.query.filter_by(user_id=current_user.id).all()
    return render_template('view_portfolio.html', title='My Portfolio', sections=sections)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)