#!/usr/bin/python3
from models import storage
from models.user import User
from models.course import Course
from models.exam import Exam
from models.student_course import StudentCourse
from models.responses import QuestionResponse
from models.answer import Answer
from models.result import Result
from models.question import Question
from models.studentlog import Studentlog
from models.passreset import PasswordResetToken
from sqlalchemy.orm import joinedload

def get_user_by_email(email):
    session = storage.get_session()
    user = session.query(User).filter_by(Email = email).first()
    session.close()
    return user

def get_user(user_id):
    session = storage.get_session()
    user = session.query(User).get(user_id)
    # session.close()
    return user

def get_all_user_by_email(email):
    session = storage.get_session()
    users = session.query(User).filter(User.Email == email, User.Role == 'Student').all()
    session.close()
    return users

def get_user_courses(user_id):
    session = storage.get_session()
    courses = session.query(Course).filter_by(InstructorID = user_id).all()
    session.close()
    return courses

def get_user_courses_courseid(course_id):
    session = storage.get_session()
    courses = session.query(Course).filter_by(CourseID = course_id).first()
    session.close()
    return courses

def get_one_user_course(user_id):
    session = storage.get_session()
    course = session.query(Course).filter_by(InstructorID = user_id).first()
    session.close()
    return course

def get_user_exams(course_id):
    session = storage.get_session()
    exams = session.query(Exam).filter_by(CourseID = course_id).all()
    return exams

def get_all_exams_for_instructor(instructor_id):
    session = storage.get_session()
    exams = session.query(Exam).join(Course, Exam.CourseID == Course.CourseID).filter(Course.InstructorID == instructor_id).all()
    session.close()
    return exams

def get_course(course_id):
    session = storage.get_session()
    course = session.query(Course).filter_by(CourseID = course_id).first()
    session.close()
    return course

def get_student_course(StudentID, CourseID):
    session = storage.get_session()
    student_course = session.query(StudentCourse).filter_by(StudentID=StudentID, CourseID=CourseID).first()
    session.close()
    return student_course

def get_student_courses(user_id):
    session = storage.get_session()
    courses = session.query(StudentCourse).filter_by(StudentID = user_id).all()
    return courses

def get_exam(exam_id):
    session = storage.get_session()
    exam = session.query(Exam).filter_by(ExamID = exam_id).first()
    # session.close()
    return exam

def get_hashed_password(Email):
    session = storage.get_session()
    user = session.query(User).filter(User.Email == Email).first()
    session.close()
    if user:
        return user.Password
    else:
        return None

def get_existing_response(index):
    session = storage.get_session()
    response = session.query(QuestionResponse).filter(QuestionResponse.QuestionIndex == index).first()
    session.close()
    if response:
        return response
    else:
        return None

def response_to_update(key):
    session = storage.get_session()
    response = session.query(QuestionResponse).get(key)
    session.close()
    return response

def correct_answer(questionid):
    session = storage.get_session()
    cor_answer = session.query(Answer).filter_by(QuestionID = questionid).first()
    session.close()
    return cor_answer

def user_submitted_exam(user_id, exam_id):
    session = storage.get_session()
    submitted = session.query(Result).filter_by(UserID=user_id, ExamID=exam_id).first()
    session.close()
    return submitted

def get_user_results(user_id):
    session = storage.get_session()
    results = session.query(Result).filter_by(UserID=user_id).all()
    return results

def get_exam_results(exam_id):
    session = storage.get_session()
    results = session.query(Result).filter_by(ExamID=exam_id).all()
    # session.close()
    return results

def get_questions(exam_id):
    session = storage.get_session()
    questions = session.query(Question).filter_by(ExamID=exam_id).options(joinedload(Question.answers)).all()
    return questions

def get_question(question_id):
    session = storage.get_session()
    question = session.query(Question).filter_by(QuestionID=question_id).first()
    session.close()
    return question

def get_user_by_id(user_id):
    session = storage.get_session()
    user = session.query(User).get(user_id)
    storage.close()
    return user

def get_student_exam_start_time(user_id, exam_id):
    session = storage.get_session()
    start_time = session.query(Studentlog).filter_by(ExamID=exam_id, UserID=user_id).first()
    session.close()
    return start_time

def get_registered_students(course_id):
    session = storage.get_session()
    students = session.query(StudentCourse).filter_by(CourseID=course_id).all()
    session.close()
    return students

def get_student_registered(student_id, course_id):
    session = storage.get_session()
    student = session.query(StudentCourse).filter_by(StudentID = student_id, CourseID = course_id).first()
    return student

def get_token(Token):
    session = storage.get_session()
    token = session.query(PasswordResetToken).filter_by(Token = Token).first()
    # session.close()
    if token:
        return token
    else:
        return None

def get_token_user(user_id):
    session = storage.get_session()
    token = session.query(PasswordResetToken).filter_by(UserID = user_id).first()
    session.close()
    return token

def get_exam_score(exam_id, user_id):
    session = storage.get_session()
    exam_results = session.query(Result).filter_by(ExamID=exam_id, UserID=user_id).first()
    session.close()
    return exam_results