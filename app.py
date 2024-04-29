import numpy as np
from flask import Flask, render_template, request, url_for, redirect, session
from keras.models import load_model
from keras.preprocessing import image
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt
import pickle

app = Flask(__name__)

model = pickle.load(open('model.pkl','rb'))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

db = SQLAlchemy(app)
app.secret_key = 'secret_key'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


with app.app_context():
    db.create_all()


@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/predict',methods=['POST'])
def predict():
    input_text = request.form['text']
    input_text_sp = input_text.split(',')
    np_data = np.asarray(input_text_sp, dtype=np.float32)
    prediction = model.predict(np_data.reshape(1,-1))

    if prediction == 1:
        output = "This person has a parkinson disease"
    else:
        output = "this person has no parkinson disease"

    return render_template("index.html", message= output)

# routes
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/main", methods=['GET', 'POST'])
def main():
    return render_template("index.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        user = User.query.filter_by(username=name).first()

        if user and user.check_password(password):
            session['name'] = user.username
            session['password'] = user.password
            return render_template('index.html', username=name)

        else:
            return render_template('login.html', error='Invalid user')

    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        new_user = User(username=name, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('login')

    return render_template("register.html")


if __name__ == '__main__':
    # app.debug = True
    app.run(debug=True)
