#!/usr/bin/python3
"""flask app"""
# from flask_paginate import Markup
import flask

from models.engine import db_storage
from flask import Flask, url_for, redirect, jsonify
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
from datetime import datetime
from models.responses import QuestionResponse
# from flask_paginate import Pagination, get_page_args
import pytz
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
        elif current_user.Role == 'Student':
            return redirect(url_for('student_dashboard'))
    return flask.abort(401)

@login_required
@app.route("/student-dashboard", methods=['GET'], strict_slashes=False)
def student_dashboard():
    if current_user.is_authenticated and current_user.Role == 'Student':
        student_courses = query_functions.get_student_courses(current_user.get_identification())
        available_exams = []
        for course in student_courses:
            # print(course.CourseID)
            exams = query_functions.get_user_exams(course.CourseID)
            # for exam in exams:
            # exam_coursename = []
            # for exam in exams:
            #     exam_course = exam.CourseID
            #     coursename = query_functions.get_user_courses_courseid(exam_course)
            #     print(coursename.CourseName)
            #     exam_coursename.append(coursename)
            available_exams.extend(exams)
            #     available_exams = exam.Title
        return render_template("Student-dashboard.html", exams=available_exams)
    else:
        flask.abort(401)

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
    if current_user.is_authenticated and current_user.Role == 'Instructor':
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
    else:
        flask.abort(401)

@login_required
@app.route("/dashboard/view-courses", methods=['GET'], strict_slashes=False)
def view_courses():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
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
    else:
        flask.abort(401)

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
    if current_user.is_authenticated and current_user.Role == 'Instructor':
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
            # StartTime = request.form['start_time']
            # Duration = request.form['duration']
            #
            # exam = Exam(CourseID=CourseID, Title=Title, StartTime=StartTime, Duration=Duration)

            local_start_time = request.form['start_time']
            local_timezone = pytz.timezone(request.form['detected_timezone'])
            local_datetime = datetime.strptime(local_start_time, '%Y-%m-%dT%H:%M')
            local_datetime = local_timezone.localize(local_datetime)
            utc_start_time = local_datetime.astimezone(pytz.utc)
            Duration = request.form['duration']

            exam = Exam(CourseID=CourseID, Title=Title, StartTime=utc_start_time, Duration=Duration)
            storage.new(exam)
            storage.save()
            return redirect(url_for('view_courses'))
    else:
        flask.abort(401)

@login_required
@app.route("/dashboard/view-courses/delete_exam/<int:exam_id>", methods=['GET'], strict_slashes=False)
def delete_exam(exam_id):
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        exam_to_delete = query_functions.get_exam(exam_id)
        if exam_to_delete:
            storage.delete(exam_to_delete)
            storage.save()
        return redirect(url_for('view_courses'))
    else:
        flask.abort(401)

@login_required
@app.route("/dashboard/questions-template", methods=['GET', 'POST'])
def add_question():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())
        courses = query_functions.get_user_courses(current_user.get_identification())
        if request.method == 'POST':
            ExamID = request.form['select-exam']
            # ExamID = request.form['ExamID']
            QuestionText = request.form['question_text']
            QuestionType = request.form['question_type']
            # print(QuestionType)
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
    else:
        flask.abort(401)



    # exams = query_functions.get_all_exams_for_instructor(current_user.get_identification())
    # courses = query_functions.get_user_courses(current_user.get_identification())
    # if courses:
    #     for course in courses:
    #         print(course.CourseName)
    # if exams:
    #     for exam in exams:
    #         print(exam.CourseID)


# students search by email
@login_required
@app.route("/dashboard/search_students_by_email")
def search_students_by_email():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        search_email = request.args.get("email")
        students = query_functions.get_all_user_by_email(search_email)
        # print(students)
        serialized_students = []
        serialized_students = [
            {"id": student.UserID, "FirstName": student.FirstName, "LastName": student.LastName, "Email": student.Email}
            for student in students
        ]
        serialized = jsonify(serialized_students)
        return serialized
    else:
        flask.abort(401)
    # return render_template("Register_students.html", students=serialized)

@login_required
@app.route("/dashboard/register_students_template", methods=['GET', 'POST'])
def register_students_template():
    if current_user.is_authenticated and current_user.Role == 'Instructor':
        available_courses = query_functions.get_user_courses(current_user.get_identification())
        error = ""
        if request.method == 'POST':
            StudentID = request.form['student_id']
            CourseID = request.form['course_id']

            existing_registration = query_functions.get_student_course(StudentID, CourseID)
            if existing_registration:
                error = "Student already registered to this course."
                return render_template("Register_students.html", courses=available_courses, error=error)

            studentcourse = StudentCourse(StudentID=StudentID, CourseID=CourseID)
            storage.new(studentcourse)
            storage.save()
            return redirect(url_for('register_students_template'))
        else:
            return render_template("Register_students.html", courses=available_courses, error=error)
    else:
        flask.abort(401)

# @login_required
# @app.route("/take_exam/<int:exam_id>", methods=['GET', 'POST'])
# @app.route("/take_exam/<int:exam_id>/<int:page>", methods=['GET', 'POST'])
# def take_exam(exam_id, page=1):
#     page = request.args.get('page', 1, type=int)
#     if current_user.is_authenticated and current_user.Role == 'Student':
#         exam = query_functions.get_exam(exam_id)
#         if exam:
#             questions = exam.questions
#             for question in questions:
#                 print(question.QuestionText)
#             total_questions = len(questions)
#
#             per_page = 1  # Number of questions per page
#             start_idx = (page - 1) * per_page
#             end_idx = start_idx + per_page
#             paginated_questions = questions[start_idx:end_idx]
#
#             pagination = Pagination(
#                 page=page,
#                 per_page=per_page,
#                 total=total_questions
#             )
#
#             if request.method == 'POST':
#             #     selected_answer = request.form.get('answer')
#             #     # Process and store student's answer for the current question
#             #
#             # # if request.form and page > 1:
#             #     # return redirect(url_for('take_exam', exam_id=exam_id, page=page))
#                 if request.form and page < total_questions:
#                     return redirect(url_for('take_exam', exam_id=exam_id, page=page + 1))
#                 else:
#                     return redirect(url_for('take_exam', exam_id=exam_id, page=page - 1))
#                         # return redirect(url_for('exam_results', exam_id=exam_id))
#
#             return render_template("Take-exam.html", exam=exam, paginated_questions=paginated_questions, pagination=pagination, page=page)
#     return redirect(url_for('student_dashboard'))

# @app.route("/take_exam/<int:exam_id>", methods=['GET', 'POST'])
# def take_exam(exam_id):
#     if current_user.is_authenticated and current_user.Role == 'Student':
#         exam = query_functions.get_exam(exam_id)
#         if exam:
#             questions = exam.questions
#
#             if request.method == 'POST':
#                 # Process and store student's answers
#                 student_answers = {}
#                 for question in questions:
#                     answer_key = f'answer_{question.QuestionID}'
#                     selected_answer = request.form.get(answer_key)
#                     student_answers[question.QuestionID] = selected_answer
#                     # Store or process the student's answer as needed
#
#                 # Calculate the student's score and perform any other required calculations
#
#                 # Redirect to the exam results page
#                 return redirect(url_for('exam_results', exam_id=exam_id))
#
#             return render_template("Take-exam.html", exam=exam, questions=questions)
#     return redirect(url_for('student_dashboard'))

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
                    questions = exam.questions
                    total_questions = len(questions)
                    # print(total_questions)

                    # Get the current question index from query parameter
                    question_index = int(0) # int(request.args.get('question_index', 0))

                    # Get the question for the current index


                    # if request.method == 'POST':
                        # Process and store student's answers
                        # ...
                        # next_question_index = question_index + 1
                        #
                        # if 'next' in request.form and next_question_index < total_questions:
                        #     if 'answer' in request.form:
                        #         selected_ans = request.form['answer']
                        #         index = next_question_index - 1
                        #         # selected_answers[index] = selected_ans
                        #         print(index)
                        #         print(selected_ans)
                        #         user = current_user.get_identification()
                        #         existing = query_functions.get_existing_response(index)
                        #         if existing:
                        #             try:
                        #                 response_id = query_functions.response_to_update(existing.ResponseID)
                        #                 # print(existing.ResponseID)
                        #                 # print(response_id.Response, response_id.QuestionIndex)
                        #                 response_id.Response = f'{selected_ans}'
                        #                 storage.save()
                        #                 # print(response_id.Response, response_id.ResponseID)
                        #             except Exception as e:
                        #                 print("errorrrrrrr")
                        #
                        #         else:
                        #             response = QuestionResponse(UserID=user, QuestionIndex=index, ExamID=exam_id, Response=selected_ans )
                        #             storage.new(response)
                        #             storage.save()

                            # Redirect to the next question
                        #         return redirect(url_for('take_exam', exam_id=exam_id, question_index=next_question_index,
                        #                             total_questions=total_questions))
                        # elif 'back' in request.form:
                        #     print('done')
                        #     prev_question_index = max(0, question_index - 1)
                        #     return redirect(url_for('take_exam', exam_id=exam_id, question_index=prev_question_index,
                        #                             total_questions=total_questions))

                        # Calculate the index for the next question
                        # elif next_question_index == total_questions:
                        #     return return redirect(url_for('take_exam', exam_id=exam_id, question_index=next_question_index))
                        # else:
                        #     # Redirect to exam results or completion page
                        #     return redirect(url_for('thank_you', exam_id=exam_id))

                    # question = questions[question_index]
                    # Render the question page template
                    return render_template("Take-exam.html", questions=questions, question_index=question_index)
                return render_template("Take-exam.html", questions=questions, question_index=question_index)
            else:
                flask.abort(401)

    # return redirect(url_for('student_dashboard'))
    elif request.method == 'POST':
        # return render_template("Take-exam.html", questions=questions, question_index=question_index)
        if current_user.is_authenticated and current_user.Role == 'Student':
            exam = query_functions.get_exam(exam_id)
            selected_answers = {}
            # storage.get_session()
            exam = query_functions.get_exam(exam_id)
            for question in exam.questions:
                question_id = question.QuestionID
                selected_answer = request.form.get(f'answer_{question_id}')
                selected_answers[question_id] = selected_answer
                print(selected_answers[question_id])
                # for question_id, selected_answer in selected_answers.items():
                #     print(f"Question ID: {question_id}, Selected Answer: {selected_answer}")
            # storage.get_session()
            questions = exam.questions
            total_questions = len(questions)
            correct_answers = {}

            for question in questions:
                answer = query_functions.correct_answer(question.QuestionID)
                correct_answers[question.QuestionID] = answer.CorrectAnswer
                # print(correct_answers[question.QuestionID])
                # Store selected answers in the database or a temporary storage
                # (e.g., in-memory data structure, session, etc.)

            correct_count = 0
            for question_id, selected_answer in selected_answers.items():
                if selected_answer == correct_answers[question_id]:
                    correct_count += 1

            score_percentage = (correct_count / total_questions) * 100
            print(int(score_percentage),"%")

            result = Result(ExamID=exam_id, UserID=current_user.get_identification(),
                            score=score_percentage, Timestamp=datetime.now())
            storage.new(result)
            storage.save()

            return redirect(url_for('thank_you'))
        else:
            flask.abort(401)

# def calculate_student_score(exam, selected_answers):
#     correct_answers = {}  # Dictionary to store correct answers
#     for question in exam.questions:
#         correct_answers[question.QuestionID] = question.correct_answer
#
#     score = 0
#     for question_id, selected_answer in selected_answers.items():
#         if selected_answer == correct_answers[question_id]:
#             score += 1
#
#     return score

@login_required
@app.route("/exam_results", strict_slashes=False)
def exam_results():
    if current_user.is_authenticated and current_user.Role == 'Student':
        user_results = query_functions.get_user_results(current_user.get_identification())
        return render_template("Results.html", results=user_results)

@app.route("/take_exam/submission", strict_slashes=False)
def thank_you():
    return redirect(url_for('exam_results'))


# @app.route("/take_exam/<int:exam_id>", methods=['GET', 'POST'])
# def take_exam(exam_id):
#     if current_user.is_authenticated and current_user.Role == 'Student':
#         exam = query_functions.get_exam(exam_id)
#         if exam:
#             questions = exam.questions
#             total_questions = len(questions)
#
#             # Get current page number and items per page from query parameters
#             page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
#
#             # Calculate the start and end indices for the current page
#             start_idx = (page - 1) * per_page
#             end_idx = start_idx + per_page
#
#             # Get the questions for the current page
#             paginated_questions = questions[start_idx:end_idx]
#
#             pagination = Pagination(
#                 page=page,
#                 per_page=per_page,
#                 total=total_questions,
#                 # css_framework='bootstrap',  # Use Bootstrap styling
#                 display_msg='Displaying questions {start} - {end} of {total}'
#             )
#
#             if request.method == 'POST':
#                 # Process and store student's answers
#                 # for question in paginated_questions:
#                 #     answer = request.form.get(f'answer_{question.QuestionID}')
#                     # Store or process the answer as needed
#
#                 if page < total_questions // per_page:
#                     return redirect(url_for('take_exam', exam_id=exam_id, page=page + 1))
#                 else:
#                     return redirect(url_for('exam_results', exam_id=exam_id))
#
#             return render_template("Take-exam.html", exam=exam, paginated_questions=paginated_questions,
#                                    pagination=pagination)
#     return redirect(url_for('student_dashboard'))

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)