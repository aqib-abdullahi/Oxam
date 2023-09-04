#!/usr/bin/python3
"""This module takes the student course class"""
from models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, DateTime

class StudentCourse(Base):
    """defines StudentCourse with attributes"""
    __tablename__ = 'StudentCourses'

    StudentCourseID = Column(Integer, primary_key=True)
    StudentID = Column(Integer, ForeignKey('Users.UserID'))
    CourseID = Column(Integer, ForeignKey('Courses.CourseID'))

    """Relationships"""
    student = relationship("User", back_populates="registered_courses")
    course = relationship("Course", back_populates="registered_students")

    def __init__(self, StudentID, CourseID):
        self.StudentID = StudentID
        self.CourseID = CourseID