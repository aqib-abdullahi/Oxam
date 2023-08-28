#!/usr/bin/python3
"""flask app"""
import flask
from flask import Flask, url_for, redirect
from flask import render_template, request
from models import storage
from models.user import User
from models.course import Course
from models.exam import Exam
from models.question import Question
from models.answer import Answer
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from models.engine import query_functions
from passlib.hash import bcrypt_sha256
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'signin'

@login_manager.user_loader
def user_loader(user_id):
    return query_functions.get_user_by_email(user_id)

# login_manager.user_loader(load_user)

@app.route("/Signup", methods = ['GET', 'POST'], strict_slashes=False)
def add_user():
    Repeat_password = None
    if request.method == 'POST':
        FirstName = request.form['First name']
        LastName = request.form['Last name']
        Email = request.form['Email Address']
        # UserName = request.form['UserName']
        Password = request.form['Password']
        Repeat_password = request.form['Repeat_password']
        Role = request.form['Role']

        hashed_password = bcrypt_sha256.hash(Password)
        error = None
        form_data = {}
        existing_email = query_functions.get_user_by_email(Email)
        # existing_username = query_functions.get_user_by_username(UserName)
        if existing_email:
            error = "Email address already in use!"
            form_data = {
                'FirstName' : FirstName,
                'LastName' : LastName,
                # 'UserName' : UserName,
                'Role' : Role
            }
            return render_template("Signup.html", error=error, form_data=form_data)
        # elif existing_username:
        #     error = "Username already taken!"
        #     form_data = {
        #         'FirstName': FirstName,
        #         'LastName': LastName,
        #         'Email': Email,
        #         'Role': Role
        #     }
        #     return render_template("Signup.html", error=error, form_data=form_data)
        elif Repeat_password != Password :
            error = "Password and repeat password doesn't match"
            form_data = {
                'FirstName': FirstName,
                'LastName': LastName,
                # 'UserName': UserName,
                'Email': Email,
                'Role': Role
            }
            return render_template("Signup.html", error=error, form_data=form_data)
        else:
            user = User(FirstName=FirstName, LastName=LastName, Email=Email,
                        Password=hashed_password, Role=Role, authenticated=False)
            storage.new(user)
            storage.save()
            return redirect(url_for('signin'))
    return render_template("Signup.html", error=None, form_data={})

@app.route("/Signin", methods=['GET', 'POST'], strict_slashes=False)
def signin():
    error = None
    form_data = {}
    if request.method == 'POST':
        Email = request.form['Email']
        Password = request.form['Password']

        user = query_functions.get_user_by_email(Email)
        if user:
            hashed_password_from_db = query_functions.get_hashed_password(Email)
            validity = bcrypt_sha256.verify(Password, hashed_password_from_db)
            if validity:
                user.authenticated = True
                storage.new(user)
                storage.save()
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid email or password!"
                form_data = {
                    'Email' : Email
                }
                return render_template("Login.html", form_data=form_data, error=error)
        else:
            error = "Invalid email or password!"
            form_data = {
                'Email': Email
            }
            return render_template("Login.html", form_data=form_data, error=error)

    return render_template("Login.html", form_data=form_data, error=error)

@login_required
@app.route("/dashboard", methods=['GET'], strict_slashes=False)
def dashboard():
    if current_user.is_authenticated:
        if current_user.Role == 'Instructor':
            return render_template("Instructor-dashboard.html")
    return flask.abort(401)

@login_required
@app.route("/logout", strict_slashes=False)
def logout():
    if current_user.is_authenticated:
        user = current_user
        user.authenticated = False
        storage.new(user)
        storage.save()
        logout_user()
        return redirect(url_for('signin'))
    return flask.abort(401)

# for instructors
@login_required
@app.route("/dashboard/create_course", strict_slashes=False , methods=['GET', 'POST'])
def create_course_form():
    if request.method == 'POST':
        course_code = request.form['course_code']
        course_name = request.form['course_name']
        course_description = request.form['course_description']

        course = Course(CourseCode=course_code, InstructorID=current_user.get_identification(),
                        CourseName=course_name, Description=course_description)
        storage.new(course)
        storage.save()
        return redirect(url_for('view_courses'))

    return render_template('create_course.html')

@login_required
@app.route("/dashboard/view-courses", methods=['GET'], strict_slashes=False)
def view_courses():
    courses = query_functions.get_user_courses(current_user.get_identification())
    # one_course = query_functions.get_one_user_course(current_user.get_identification())
    # print(one_course.CourseID)
    # course_identification = one_course.CourseID
    # print(course_identification)
    exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())
        # exams = query_functions.get_user_exams(course_identification)
        # exams_dict = {}
        # for exam in exams:
        #     course_id = exam.CourseID
        #     if course_id not in exams_dict:
        #         exams_dict[course_id] = []
        #     exams_dict[course_id].append(exam)
    # return render_template("view_course.html", courses=courses, exams=exams)

    return render_template("view_course.html", courses=courses, exams=exams)

@login_required
@app.route("/dashboard/view-courses/delete_course/<int:course_id>", methods=['GET'], strict_slashes=False)
def delete_course(course_id):
    course_to_delete = query_functions.get_course(course_id)
    if course_to_delete:
        storage.delete(course_to_delete)
        storage.save()
        return redirect(url_for('view_courses'))

    return redirect(url_for('view_courses'))

@login_required
@app.route("/dashboard/create_exam", methods=['GET', 'POST'], strict_slashes=False)
@app.route("/dashboard/create_exam/<int:course_id>", methods=['GET', 'POST'], strict_slashes=False)
def create_exam(course_id=None):
    if request.method == 'GET':
        available_courses = query_functions.get_user_courses(current_user.get_identification())
        course_exam = None
        if course_id:
            course_exam = query_functions.get_course(course_id)
            return render_template("create_exam.html", available_courses=available_courses, course_exam=course_exam)
        # if course_id:
        #     return render_template("create_exam.html", available_courses=available_courses, course_exam=course_exam)
        # else:
        #     course_exam = None
        return render_template("create_exam.html", available_courses=available_courses, course_exam=course_exam)
    elif request.method == 'POST':
        CourseID = request.form['selected-course-id']
        Title = request.form['exam_title']
        StartTime = request.form['start_time']
        Duration = request.form['duration']

        exam = Exam(CourseID=CourseID, Title=Title, StartTime=StartTime, Duration=Duration)
        storage.new(exam)
        storage.save()
        return redirect(url_for('view_courses'))

@login_required
@app.route("/dashboard/view-courses/delete_exam/<int:exam_id>", methods=['GET'], strict_slashes=False)
def delete_exam(exam_id):
    exam_to_delete = query_functions.get_exam(exam_id)
    if exam_to_delete:
        storage.delete(exam_to_delete)
        storage.save()
    return redirect(url_for('view_courses'))

@login_required
@app.route("/dashboard/questions-template", methods=['GET', 'POST'])
def add_question():
    exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())
    courses = query_functions.get_user_courses(current_user.get_identification())
    if request.method == 'POST':
        ExamID = request.form['select-exam']
        # ExamID = request.form['ExamID']
        QuestionText = request.form['question_text']
        QuestionType = request.form['question_type']
        print(QuestionType)
        if QuestionType == "MultipleChoice":
            options = [
                request.form['option_1'],
                request.form['option_2'],
                request.form['option_3'],
                request.form['option_4'],
                request.form['option_5'],
            ]
        else:
            options = [
                request.form['option_1'],
                request.form['option_2'],
            ]

        correct_answer = request.form['correct_answer']
        question = Question(ExamID=ExamID, QuestionText=QuestionText, QuestionType=QuestionType)

        for idx, option_text in enumerate(options):
            answer = Answer(QuestionID=question.QuestionID,
                            AnswerText=option_text,
                            CorrectAnswer=correct_answer)
            question.answers.append(answer)

        storage.new(question)
        storage.save()

        return redirect(url_for('add_question'))

    return render_template("Questions_template.html", exams=exams, courses=courses)



    # exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())
    # courses = query_functions.get_user_courses(current_user.get_identification())
    # if courses:
    #     for course in courses:
    #         print(course.CourseName)
    # if exams:
    #     for exam in exams:
    #         print(exam.CourseID)


@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)