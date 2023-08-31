#!/usr/bin/python3
"""Module for responses"""
from models.base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

class QuestionResponse(Base):
    """Defines the QuestionResponse class to store student's responses"""
    __tablename__ = "QuestionResponses"

    ResponseID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey('Users.UserID'))  # Add User foreign key
    QuestionIndex = Column(Integer)
    ExamID = Column(Integer, ForeignKey('Exams.ExamID'))
    # QuestionID = Column(Integer, ForeignKey('Questions.QuestionID'))
    Response = Column(Text)

    """Relationships"""
    # question = relationship("Question", back_populates="responses")
    user = relationship("User", back_populates="question_responses")  # Add User relationship
    exams = relationship("Exam", back_populates="responses")

    def __init__(self, UserID, QuestionIndex, Response, ExamID):
        self.UserID = UserID
        # self.ResultID = ResultID
        self.QuestionIndex = QuestionIndex
        self.ExamID = ExamID
        self.Response = Response
        # self.QuestionID = QuestionID