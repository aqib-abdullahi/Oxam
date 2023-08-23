#!/usr/bin/python3
"""flask app"""
from flask import Flask, url_for, redirect
from flask import render_template, request
from models import storage
from models.user import User
from models.engine import query_functions

app = Flask(__name__)

@app.route("/Signup", methods = ['GET', 'POST'])
def add_user():
    Repeat_password = None
    if request.method == 'POST':
        FirstName = request.form['First name']
        LastName = request.form['Last name']
        Email = request.form['Email Address']
        UserName = request.form['UserName']
        Password = request.form['Password']
        Repeat_password = request.form['Repeat_password']
        Role = request.form['Role']

        error = None
        form_data = {}
        existing_email = query_functions.get_user_by_email(Email)
        existing_username = query_functions.get_user_by_username(UserName)
        if existing_email:
            error = "Email address already in use!"
            form_data = {
                'FirstName' : FirstName,
                'LastName' : LastName,
                'UserName' : UserName,
                'Role' : Role
            }
            return render_template("Signup.html", error=error, form_data=form_data)
        elif existing_username:
            error = "Username already taken!"
            form_data = {
                'FirstName': FirstName,
                'LastName': LastName,
                'Email': Email,
                'Role': Role
            }
            return render_template("Signup.html", error=error, form_data=form_data)
        elif Repeat_password != Password :
            error = "Password and repeat password doesn't match"
            form_data = {
                'FirstName': FirstName,
                'LastName': LastName,
                'UserName': UserName,
                'Email': Email,
                'Role': Role
            }
            return render_template("Signup.html", error=error, form_data=form_data)
        else:
            user = User(FirstName=FirstName, LastName=LastName, Email=Email, UserName=UserName, Password=Password, Role=Role)
            storage.new(user)
            storage.save()
            return redirect(url_for('signin'))
    return render_template("Signup.html", error=None, form_data={})

@app.route("/Signin", methods=['GET'])
def signin():
    return "signed in"

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)