from flask import Flask, render_template
from flask_bootstrap import Bootstrap5
from forms import SignUpForm


app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = 'asdfjalskdjfaklj'

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signup")
def signup():
    form = SignUpForm()
    return render_template('signup.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
