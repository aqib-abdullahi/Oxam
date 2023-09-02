#!/usr/bin/python3
"""flask app"""
from flask import Flask, url_for, redirect, jsonify, flash, session
import flask
from flask import render_template, request
from models import storage
from models.user import User
from models.course import Course
from models.exam import Exam
from models.question import Question
from models.answer import Answer
from models.student_course import StudentCourse
from models.result import Result
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from models.engine import query_functions
from passlib.hash import bcrypt_sha256
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pytz
import os

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def user_loader(user_id):
    return query_functions.get_user_by_email(user_id)

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
        if existing_email:
            error = "Email address already in use!"
            form_data = {
                'FirstName' : FirstName,
                'LastName' : LastName,
                'Role' : Role
            }
            return render_template("Signup.html", error=error, form_data=form_data)
        elif Repeat_password != Password :
            error = "Password and repeat password doesn't match"
            form_data = {
                'FirstName': FirstName,
                'LastName': LastName,
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
                login_user(user, remember=False)
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
        elif current_user.Role == 'Student':
            return redirect(url_for('student_dashboard'))

    # return flask.abort(401)
    return redirect(url_for('signin'))

@login_required
@app.route("/student-dashboard", methods=['GET'], strict_slashes=False)
def student_dashboard():
    if current_user.is_authenticated and current_user.Role == 'Student':
        student_courses = query_functions.get_student_courses(current_user.get_identification())
        available_exams = []
        for course in student_courses:
            exams = query_functions.get_user_exams(course.CourseID)
            available_exams.extend(exams)
        return render_template("Student-dashboard.html", exams=available_exams)
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

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

    return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/create_course", strict_slashes=False , methods=['GET', 'POST'])
def create_course_form():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        current_page = "Create Course"
        if request.method == 'POST':
            course_code = request.form['course_code']
            course_name = request.form['course_name']
            course_description = request.form['course_description']
            course = Course(CourseCode=course_code, InstructorID=current_user.get_identification(),
                            CourseName=course_name, Description=course_description)
            storage.new(course)
            storage.save()
            flash('Course successfully created', 'success')
            return redirect(url_for('view_courses'))

        return render_template('create_course.html', current_page=current_page)
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/view-courses", methods=['GET'], strict_slashes=False)
def view_courses():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        current_page  = "View courses"
        courses = query_functions.get_user_courses(current_user.get_identification())
        exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())

        return render_template("view_course.html", courses=courses, exams=exams, current_page=current_page)
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@app.route("/dashboard/view-results", methods=["GET", "POST"])
@login_required
def view_students_results():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        current_page = "Exam performance"
        if request.method == "POST":
            course_id = request.form['course_id']
            exam_id = request.form["exam_id"]
            results = query_functions.get_exam_results(exam_id)
            return render_template("instructor-exam-results.html", results=results, current_page=current_page)
        else:
            courses = query_functions.get_user_courses(current_user.get_identification())
            return render_template("Instructor-results-form.html", courses=courses, current_page=current_page)
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route('/get_exams_for_course')
def get_exams_for_course():
    course_id = request.args.get('course_id')
    exams  = query_functions.get_user_exams(course_id)
    exams_data = [{'ExamID': exam.ExamID, 'Title': exam.Title} for exam in exams]
    return jsonify({'exams': exams_data})



@login_required
@app.route("/dashboard/view-courses/delete_course/<int:course_id>", methods=['GET'], strict_slashes=False)
def delete_course(course_id):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        course_to_delete = query_functions.get_course(course_id)
        if course_to_delete:
            storage.delete(course_to_delete)
            storage.save()
            flash('Course successfully deleted', 'success')
            return redirect(url_for('view_courses'))

        return redirect(url_for('view_courses'))
    else:
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/view-course/view-questions/<int:exam_id>", methods=['GET', 'POST'], strict_slashes=False)
def view_questions(exam_id):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        questions = query_functions.get_questions(exam_id)
        questionid = query_functions.get_exam(exam_id)
        questionid = questionid.ExamID
        current_page = "View courses"
        return render_template("Created-questions.html", questions=questions, questionid=questionid, current_page=current_page)
    else:
        return redirect(url_for('signin'))

@login_required
@app.route('/dashboard/view-courses/view-questions/delete_question/<int:exam_id>/<int:question_id>', methods=['POST'])
def delete_question(question_id, exam_id):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        question = query_functions.get_question(question_id)
        questions = query_functions.get_questions(exam_id)
        current_page = "View courses"
        if question:
            storage.delete(question)
            storage.save()
            flash('Question deleted successfully', 'success')
            return redirect(url_for('view_questions', questions=questions, exam_id=exam_id, current_page=current_page))
        else:
            flash('Question not found', 'error')
            return redirect(url_for('view_questions', questions=questions, current_page=current_page))
    else:
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/create_exam", methods=['GET', 'POST'], strict_slashes=False)
@app.route("/dashboard/create_exam/<int:course_id>", methods=['GET', 'POST'], strict_slashes=False)
def create_exam(course_id=None):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        current_page = "Create Exam"
        if request.method == 'GET':
            available_courses = query_functions.get_user_courses(current_user.get_identification())
            course_exam = None
            if course_id:
                course_exam = query_functions.get_course(course_id)
                return render_template("create_exam.html", available_courses=available_courses, course_exam=course_exam, current_page=current_page)

            return render_template("create_exam.html", available_courses=available_courses, course_exam=course_exam, current_page=current_page)
        elif request.method == 'POST':
            CourseID = request.form['selected-course-id']
            Title = request.form['exam_title']
            local_start_time = request.form['start_time']
            local_timezone = pytz.timezone(request.form['detected_timezone'])
            local_datetime = datetime.strptime(local_start_time, '%Y-%m-%dT%H:%M')
            local_datetime = local_timezone.localize(local_datetime)
            utc_start_time = local_datetime.astimezone(pytz.utc)
            Duration = request.form['duration']
            exam = Exam(CourseID=CourseID, Title=Title, StartTime=utc_start_time, Duration=Duration)
            storage.new(exam)
            storage.save()
            flash('Exam successfully created', 'success')
            return redirect(url_for('view_courses'))
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/view-courses/delete_exam/<int:exam_id>", methods=['GET'], strict_slashes=False)
def delete_exam(exam_id):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        exam_to_delete = query_functions.get_exam(exam_id)
        if exam_to_delete:
            storage.delete(exam_to_delete)
            storage.save()
            flash('Exam successfully deleted', 'success')
        return redirect(url_for('view_courses'))
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/questions-template/<int:exam_id>", methods=['GET', 'POST'])
@app.route("/dashboard/questions-template", methods=['GET', 'POST'])
def add_question(exam_id=None):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        current_page = "Question Template"
        exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())
        courses = query_functions.get_user_courses(current_user.get_identification())
        if request.method == 'POST':
            ExamID = request.form['select-exam']
            QuestionText = request.form['question_text']
            QuestionType = request.form['question_type']
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
            flash('Question successfully created', 'success')
            return redirect(url_for('add_question', current_page=current_page))

        examination_id = exam_id
        return render_template("Questions_template.html", exams=exams, courses=courses, examination_id=examination_id, current_page=current_page)
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/search_students_by_email")
def search_students_by_email():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        search_email = request.args.get("email")
        students = query_functions.get_all_user_by_email(search_email)
        serialized_students = []
        serialized_students = [
            {"id": student.UserID, "FirstName": student.FirstName, "LastName": student.LastName, "Email": student.Email}
            for student in students
        ]
        serialized = jsonify(serialized_students)
        return serialized
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route("/dashboard/register_students_template", methods=['GET', 'POST'])
def register_students_template():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        current_page = "Register Student"
        available_courses = query_functions.get_user_courses(current_user.get_identification())
        error = ""
        if request.method == 'POST':
            StudentID = request.form['student_id']
            CourseID = request.form['course_id']

            existing_registration = query_functions.get_student_course(StudentID, CourseID)
            if existing_registration:
                error =  "" #Student already registered to this course.
                flash('Student already registered', 'error')
                return render_template("Register_students.html", courses=available_courses, current_page=current_page)

            studentcourse = StudentCourse(StudentID=StudentID, CourseID=CourseID)
            storage.new(studentcourse)
            storage.save()
            flash('Student successfully registered', 'success')
            return redirect(url_for('register_students_template', current_page=current_page))
        else:
            return render_template("Register_students.html", courses=available_courses, current_page=current_page)
    else:
        # flask.abort(401)
        return redirect(url_for('signin'))

@login_required
@app.route("/take_exam/<int:exam_id>", methods=['GET', 'POST'])
def take_exam(exam_id):
    if request.method == 'GET':
        if current_user.is_authenticated and current_user.Role == 'Student':
            submitted = query_functions.user_submitted_exam(current_user.get_identification(), exam_id)
            if submitted:
                return redirect(url_for('exam_results'))
            elif current_user.is_authenticated and current_user.Role == 'Student':
                exam = query_functions.get_exam(exam_id)
                if exam:
                    current_time = datetime.utcnow()
                    exam_duration = exam.Duration
                    questions = exam.questions
                    total_questions = len(questions)
                    question_index = int(0)
                    if current_time >= exam.StartTime:
                        return render_template("Take-exam.html", questions=questions, question_index=question_index, exam_duration=exam_duration)
                    else:
                        return "exam unavailable. check back later"
                else:
                    return render_template("Take-exam.html", questions=questions, question_index=question_index)
            else:
                # flask.abort(401)
                return redirect(url_for('signin'))
    elif request.method == 'POST':
        if current_user.is_authenticated and current_user.Role == 'Student':
            exam = query_functions.get_exam(exam_id)
            exam_duration = exam.Duration
            selected_answers = {}
            exam = query_functions.get_exam(exam_id)
            for question in exam.questions:
                question_id = question.QuestionID
                selected_answer = request.form.get(f'answer_{question_id}')
                selected_answers[question_id] = selected_answer
            questions = exam.questions
            total_questions = len(questions)
            correct_answers = {}

            for question in questions:
                answer = query_functions.correct_answer(question.QuestionID)
                correct_answers[question.QuestionID] = answer.CorrectAnswer
            correct_count = 0
            for question_id, selected_answer in selected_answers.items():
                if selected_answer == correct_answers[question_id]:
                    correct_count += 1

            score_percentage = (correct_count / total_questions) * 100
            result = Result(ExamID=exam_id, UserID=current_user.get_identification(),
                            score=score_percentage, Timestamp=datetime.now())
            storage.new(result)
            storage.save()

            return redirect(url_for('thank_you'))
        else:
            return redirect(url_for('signin'))

@login_required
@app.route("/student-dashboard/exam_results", strict_slashes=False)
def exam_results():
    if current_user.is_authenticated and current_user.Role == 'Student':
        user_results = query_functions.get_user_results(current_user.get_identification())
        return render_template("Results.html", results=user_results)
    else:
        return redirect(url_for('signin'))

@app.route("/take_exam/submission", strict_slashes=False)
def thank_you():
    return redirect(url_for('exam_results'))

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1440)
    session.modified = True

@login_manager.unauthorized_handler
@app.errorhandler(401)
def unauthorized(error):
    return redirect(url_for('signin'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)