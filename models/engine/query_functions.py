#!/usr/bin/python3
from models import storage
from models.user import User
from models.course import Course
from models.exam import Exam

def get_user_by_email(email):
    session = storage.get_session()
    user = session.query(User).filter_by(Email = email).first()
    session.close()
    return user

def get_user_courses(user_id):
    session = storage.get_session()
    courses = session.query(Course).filter_by(InstructorID = user_id).all()
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
    session.close()
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

def get_exam(exam_id):
    session = storage.get_session()
    exam = session.query(Exam).filter_by(ExamID = exam_id).first()
    session.close()
    return exam

# def get_user_by_email(email):
#     session = storage.get_session()
#     user = session.query(User).filter(User.Email == email).first()
#     session.close()
#     return user

def get_hashed_password(Email):
    session = storage.get_session()
    user = session.query(User).filter(User.Email == Email).first()
    session.close()
    if user:
        return user.Password
    else:
        return None