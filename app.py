import os
from flask import Flask, request, jsonify, render_template, redirect
from models import db, connect_db, User
from dotenv import load_dotenv

def create_app(db_name, testing=False):

    ############## CONFIG ##############

    app = Flask(__name__)

    load_dotenv()
    app.testing = testing
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql:///{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('secret_key')

    ############## ROUTES ##############

    @app.route('/')
    def home():
        return redirect('/register')

    @app.route("/register", methods=["GET", "POST"])
    def register():

        form = RegisterForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            email = form.email.data
            first_name = form.first_name.data
            last_name = form.last_name.data

            user = User.register(username, password, email, first_name, last_name)
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return redirect("/secret")

        else:
            return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():

        form = LoginForm()

        if form.validate_on_submit():
            name = form.username.data
            pwd = form.password.data

            user = User.authenticate(name, pwd)

            if user:
                session["user_id"] = user.id
                return redirect("/secret")
            else:
                form.username.errors = ["Bad name/password"]

        return render_template("login.html", form=form)

    @app.route("/secret")
    def secret():
        if "user_id" not in session:
            flash("You must be logged in to view!")
            return redirect("/")
        else:
            return render_template("secret.html")

    @app.route("/logout")
    def logout():
        session.pop("user_id")
        return redirect("/")

    return app

############## CREATE APP/CONNECT DB ##############

if __name__ == '__main__':
    app = create_app('users')
    connect_db(app)
    app.run(debug=True)