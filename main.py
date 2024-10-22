from flask import Flask, render_template, request, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from forms import SignUpForm, LoginForm, CategoryForm, QuestionForm, PopulateForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from functools import wraps
from datetime import datetime
import requests, random, html

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
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    quiz = relationship("Quiz", back_populates="user")

class Category(db.Model):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    category_name: Mapped[str] = mapped_column(String(250),nullable=False)
    api_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))
    questions = relationship("Questions", back_populates="category",cascade="all, delete-orphan")
    attempts = relationship("Quiz", back_populates='category')

class Questions(db.Model):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    question_text : Mapped[str] = mapped_column(String(300),nullable=False)
    category = relationship("Category", back_populates="questions")
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))
    options = relationship("Options", back_populates="question",cascade="all, delete-orphan")

    
class Options(db.Model):
    __tablename__ = 'options'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question = relationship("Questions", back_populates="options")
    question_id : Mapped[int] = mapped_column(Integer, ForeignKey("questions.id"))
    option_text : Mapped[str] = mapped_column(String(250), nullable=False)
    is_correct : Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Quiz(db.Model):
    __tablename__ = "quiz"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user = relationship("User", back_populates='quiz')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))
    category = relationship("Category", back_populates='attempts')
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"))
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    score: Mapped[int] = mapped_column(Integer, nullable=False)


with app.app_context():
    db.create_all()

# FLASK LOGIN
login_manager = LoginManager()
login_manager.init_app(app)

def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if current_user.id == 1:
            return function(*args,**kwargs)
        else:
            return abort(403)
    return decorated_function



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
    if form.validate_on_submit():
        if not (db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()):
            hashed_password = generate_password_hash(form.password.data, method="pbkdf2:sha256:600000",salt_length=8)
            new_user = User(name = form.username.data,
                            email= form.email.data,
                            password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('thankyou'))
        else:
            flash("Account already exist. Please login")
    return render_template('signup.html', form=form)




@app.route('/thank-you',methods=["GET","POST"])
@login_required
def thankyou():
    return render_template('thankyou.html')




@app.route("/login",methods=["GET","POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        typed_password = form.password.data
        user = db.session.execute(db.select(User).where(User.email== form.email.data)).scalar()
        if user:
            if check_password_hash(user.password, typed_password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash("Check your password and try again.")
        else:
            flash("Account doesn't exist. Please sign up!")
    return render_template("login.html", form=form)



@app.route('/dashboard',methods=["GET","POST"])
@login_required
def dashboard():
    return render_template("dashboard.html")



@app.route('/category', methods=["GET","POST"])
@login_required
def category():
    category_list = db.session.execute(db.select(Category)).scalars().all()
    return render_template('category.html',category_list=category_list)




@app.route('/manage',methods=["GET","POST"])
@admin_only
@login_required
def manage():
    form = CategoryForm()
    category_list = db.session.execute(db.select(Category)).scalars().all()
    if form.validate_on_submit():
        new_category = Category(category_name = form.category_name.data,
                                api_id = form.api_id.data)
        db.session.add(new_category)
        db.session.commit()
        flash("Successfully Added Category")
        return redirect(url_for('manage'))
    return render_template('manage.html', form=form,category_list=category_list)


@app.route("/manage-questions", methods=["GET", "POST"])
@admin_only
@login_required
def manage_questions():
    category_id = request.args.get('category_id')
    category = db.get_or_404(Category,category_id)
    return render_template("show-questions.html", category=category)

@app.route("/auto-populate", methods=["GET","POST"])
@admin_only
@login_required
def auto_populate():
    form = PopulateForm()
    api_id = request.args.get('api_id')
    if request.method == "POST":
        api_id = request.args.get('api_id')
        category = db.session.execute(db.select(Category).where(Category.api_id == api_id)).scalar()
        current_questions = db.session.execute(db.select(Questions).where(Questions.category_id == category.id)).scalars().all()
        for question in current_questions:
            db.session.delete(question)
            db.session.commit()
        quantity = form.quantity.data
        url = f"https://opentdb.com/api.php?amount={quantity}&category={api_id}&difficulty=easy&type=multiple"
        response = requests.get(url).json()
        for item in response["results"]:
            question = html.unescape(item["question"])
            correct_answer = html.unescape(item["correct_answer"])
            options = [correct_answer] + [html.unescape(item) for item in item["incorrect_answers"]]
            for option in options:
                option = html.unescape(option)
            random.shuffle(options)
            bool_values = [False,False,False,False]
            bool_values[options.index(correct_answer)] = True

            new_question = Questions(question_text = question,
                                    category_id = category.id)
            db.session.add(new_question)
            db.session.commit()
            options_to_add =[ Options(question_id = new_question.id, option_text=options[0],is_correct=bool_values[0]),
                            Options(question_id = new_question.id, option_text=options[1],is_correct=bool_values[1]),
                            Options(question_id = new_question.id, option_text=options[2],is_correct=bool_values[2]),
                            Options(question_id = new_question.id, option_text=options[3],is_correct=bool_values[3])]
            db.session.add_all(options_to_add)
            db.session.commit()
        return redirect(url_for('manage_questions', category_id=category.id))
    return render_template("populate.html", form=form, api_id=api_id)

@app.route("/add-question", methods=["GET","POST"])
@admin_only
@login_required
def add_question():
    edit = False
    form = QuestionForm()
    bool_values = [False,False,False,False]
    id = request.args.get('category_id')
    category = db.get_or_404(Category, id)
    if request.method == "POST":
        print("Helloooooo")
        bool_values[int(form.correct.data) - 1] = True
        new_question = Questions(question_text = form.question_text.data,
                                 category_id = category.id)
        db.session.add(new_question)
        db.session.commit()
        options_to_add =[ Options(question_id = new_question.id, option_text=form.option1.data,is_correct=bool_values[0]),
                         Options(question_id = new_question.id, option_text=form.option2.data,is_correct=bool_values[1]),
                         Options(question_id = new_question.id, option_text=form.option3.data,is_correct=bool_values[2]),
                         Options(question_id = new_question.id, option_text=form.option4.data,is_correct=bool_values[3])]
        db.session.add_all(options_to_add)
        db.session.commit()
        flash("Question Added Successfully")
        return redirect(url_for('manage_questions', category_id=category.id))
    return render_template('manage-question.html', category=category, form=form, edit=edit)




@app.route("/show-question", methods=["GET", "POST"])
@admin_only
@login_required
def show_question():
    edit = True
    category_id = request.args.get("category_id")
    category = db.get_or_404(Category,category_id)
    question_id = request.args.get("question_id")
    question = db.get_or_404(Questions, question_id)
    options = question.options
    correct = 0
    count = 1
    for option in options:
        if option.is_correct:
            correct = count
            break
        count+=1
    form = QuestionForm(question_text = question.question_text,
                        option1 = options[0].option_text,
                        option2 = options[1].option_text,
                        option3 = options[2].option_text,
                        option4 = options[3].option_text,
                        correct = correct
                        )
    if request.method == "POST":
        category_id = request.args.get("category_id")
        question_id = request.args.get("question_id")
        question = db.get_or_404(Questions, question_id)
        question.question_text = form.question_text.data
        db.session.commit()
        bool_values = [False,False,False,False]
        options[0].option_text = form.option1.data
        options[1].option_text = form.option2.data
        options[2].option_text = form.option3.data
        options[3].option_text = form.option4.data
        bool_values[int(form.correct.data) - 1] = True
        for i in range(4):
            options[i].is_correct = bool_values[i]
        db.session.commit()
        return redirect(url_for('manage_questions', category_id=category_id))
    return render_template('manage-question.html', form=form, category=category,question_id=question_id, edit=True)


@admin_only
@app.route('/delete_category',methods=["GET","POST"])
@login_required
def delete_category():
    cat_id = request.args.get('category_id')
    category_to_be_deleted = db.get_or_404(Category,cat_id)
    db.session.delete(category_to_be_deleted)
    db.session.commit()
    flash('Successfully Deleted Category')
    return redirect(url_for('manage'))

@admin_only
@app.route('/delete_question',methods=["GET","POST"])
@login_required
def delete_question():
    questions_id = request.args.get('question_id')
    category_id = request.args.get('category_id')
    question_to_be_deleted = db.get_or_404(Questions,questions_id)
    db.session.delete(question_to_be_deleted)
    db.session.commit()
    flash('Successfully Deleted Question')
    return redirect(url_for('manage'))




@login_required
@app.route('/ready', methods=["GET","POST"])
def ready():
    quiz_id = request.args.get('category_id')
    return render_template('ready.html',quiz_id=quiz_id)

@login_required
@app.route('/quizzing',methods=["POST","GET"])
def quizzing():
    quiz_id = request.args.get('quiz_id')
    return render_template('quiz.html')


@app.route('/logout',methods=["POST","GET"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
