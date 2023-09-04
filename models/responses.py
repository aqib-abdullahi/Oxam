#!/usr/bin/python3
"""Module for responses"""
from models.base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

class QuestionResponse(Base):
    """Defines the QuestionResponse class to store student's responses"""
    __tablename__ = "QuestionResponses"

    ResponseID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    QuestionIndex = Column(Integer)
    ExamID = Column(Integer, ForeignKey('Exams.ExamID'))
    Response = Column(Text)

    """Relationships"""
    user = relationship("User", back_populates="question_responses")
    exams = relationship("Exam", back_populates="responses")

    def __init__(self, UserID, QuestionIndex, Response, ExamID):
        self.UserID = UserID
        self.QuestionIndex = QuestionIndex
        self.ExamID = ExamID
        self.Response = Response