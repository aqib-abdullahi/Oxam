#!/usr/bin/python3
"""defines the Exam class"""
from models.base import Base
from models.course import Course
from sqlalchemy import Column, Integer, String, VARCHAR, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

class Exam(Base):
    """defines exam with appropriate attributes"""
    __tablename__ = 'Exams'

    ExamID = Column(Integer, primary_key=True)
    CourseID = Column(Integer, ForeignKey('Courses.CourseID'))
    Title = Column(String(200))
    StartTime = Column(DateTime)
    Duration = Column(Integer)
    IsAvailable = Column(Boolean)

    """Relationships"""
    course = relationship("Course", back_populates="exams")
    results = relationship("Result", back_populates="exam", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="exam", cascade="all, delete-orphan")
    responses = relationship("QuestionResponse", back_populates="exams")
    exam_started = relationship("Studentlog", back_populates="exam", cascade="all, delete-orphan")

    def __init__(self, CourseID, Title, StartTime, Duration, IsAvailable):
        self.CourseID = CourseID
        self.Title = Title
        self.StartTime = StartTime
        self.Duration = Duration
        self.IsAvailable = IsAvailable