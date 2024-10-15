from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from forms import SignUpForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required

app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = 'asdfjalskdjfaklj'

# Database Declaration and tables

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizzify.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    email: Mapped[int] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)

with app.app_context():
    db.create_all()

# FLASK LOGIN
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#Routes

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup", methods=["POST","GET"])
def signup():
    form = SignUpForm()
    if request.method == "POST":
        if not (db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()):
            hashed_password = generate_password_hash(form.password.data, method="pbkdf2:sha256:600000",salt_length=8)
            new_user = User(name = form.username.data,
                            email= form.email.data,
                            password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            #login_user(new_user)
            return redirect(url_for('dashboard'))
        else:
            flash("Account already exist. Please login")
    return render_template('signup.html', form=form)

@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        typed_password = form.password.data
        user = db.session.execute(db.select(User).where(User.email== form.email.data)).scalar()
        if user:
            if check_password_hash(user.password, typed_password):
                #login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Check your password and try againz.")
        else:
            flash("Email doesn't exist. Please sign up!")
    return render_template("login.html", form=form)

@app.route('/dashboard',methods=["GET","POST"])
def dashboard():
    return render_template("dashboard.html")


if __name__ == '__main__':
    app.run(debug=True)
