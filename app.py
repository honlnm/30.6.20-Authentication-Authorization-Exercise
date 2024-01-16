import os
from dotenv import load_dotenv

from flask import Flask, render_template, redirect, session, flash

from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm


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

        if "username" in session:
            return redirect(f"/users/{session['username']}")

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

            session["username"] = user.username

            return redirect(f"/users/{username}")

        else:
            return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():

        if "username" in session:
            return redirect(f"/users/{session['username']}")

        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.authenticate(username, password)

            if user:
                session["username"] = user.username
                return redirect(f"/users/{user.username}")
            else:
                form.username.errors = ["Bad name/password"]
                return render_template("login.html", form=form)

        return render_template("login.html", form=form)
    
    @app.route("/logout")
    def logout():
        session.pop("username")
        return redirect("/login")

    @app.route("/users/<username>")
    def user(username):
        if "username" not in session:
            flash("You must be logged in to view!")
            return redirect("/")
        user = User.query.get(username)
        form = DeleteForm()

        return render_template("users.html", user=user, form=form)

    @app.route("/users/<username>/delete", methods=["POST"])
    def deleteAcct(username):
        if "username" not in session:
            flash("You must be logged in to view!")
            return redirect("/")
        user = User.query.get(username)
        db.session.delete(user)
        db.session.commit()
        session.pop("username")

        return redirect("/login")

    @app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
    def addFeedback(username):
        if "username" not in session:
            flash("You must be logged in to view!")
            return redirect("/")
        
        form = FeedbackForm()
        
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
        
            new_feedback = Feedback(title=title, content=content, username=username)
           
            db.session.add(new_feedback)
            db.session.commit()
           
            flash("Added Feedback")
            return redirect(f'/users/{new_feedback.username}')
        
        else:
            return render_template('addFeedback.html', form=form)

    @app.route("/feedback/<int:feedback_id>/update", methods=["GET", "POST"])
    def updateFeedback(feedback_id):

        feedback = Feedback.query.get(feedback_id)

        if "username" not in session:
            flash("You must be logged in to view!")
            return redirect("/")
    
        form = FeedbackForm(obj=feedback)
          
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            
            db.session.commit()

            flash("Feedback Updated")
            return redirect(f'/users/{feedback.username}')

        return render_template('editFeedback.html', form=form)

    @app.route("/feedback/<feedback_id>/delete", methods=["POST"])
    def deleteFeedback(feedback_id):

        feedback = Feedback.query.get(feedback_id)

        if "username" not in session:
            flash("You must be logged in to view!")
            return redirect("/")
    
        form = DeleteForm()
        
        if form.validate_on_submit():
            db.session.delete(feedback)
            db.session.commit()

        flash("Feedback Deleted")
        return redirect(f'/users/{feedback.username}')

    return app

############## CREATE APP/CONNECT DB ##############

if __name__ == '__main__':
    app = create_app('users_db')
    connect_db(app)
    app.run(debug=True)