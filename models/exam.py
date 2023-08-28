#!/usr/bin/python3
"""defines the Exam class"""
from models.base import Base
from models.course import Course
from sqlalchemy import Column, Integer, String, VARCHAR, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship

class Exam(Base):
    """defines exam with appropriate attributes"""
    __tablename__ = 'Exams'

    ExamID = Column(Integer, primary_key=True)
    CourseID = Column(Integer, ForeignKey('Courses.CourseID'))
    Title = Column(String(200))
    StartTime = Column(DateTime)
    Duration = Column(Integer)

    """Relationships"""
    course = relationship("Course", back_populates="exams")
    results = relationship("Result", back_populates="exam")
    questions = relationship("Question", back_populates="exam")

    def __init__(self, CourseID, Title, StartTime, Duration):
        self.CourseID = CourseID
        self.Title = Title
        self.StartTime = StartTime
        self.Duration = Duration