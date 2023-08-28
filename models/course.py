#!/usr/bin/python3
"""This module defines the Course class"""
from models.base import Base
from sqlalchemy import Column, Integer, String, VARCHAR, ForeignKey, Text
from sqlalchemy.orm import relationship

class Course(Base):
    """Defines course by various attributes"""
    __tablename__ = 'Courses'

    CourseID = Column(Integer, primary_key=True)
    CourseCode = Column (VARCHAR(50))
    CourseName = Column(String(100))
    InstructorID = Column(Integer, ForeignKey('Users.UserID'))
    Description = Column(Text)

    """Relationships"""
    instructor = relationship("User", back_populates="courses")
    exams = relationship("Exam", back_populates="course")

    def __init__(self, CourseCode, CourseName, Description, InstructorID):
        self.CourseCode = CourseCode
        self.CourseName = CourseName
        self.Description = Description
        self.InstructorID = InstructorID