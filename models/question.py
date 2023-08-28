#!/usr/bin/python3
"""This module defines the question class"""
from models.base import Base
from sqlalchemy import Column, Integer, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship

class Question(Base):
    """Defines Question class with appropriate attributes"""
    __tablename__ = 'Questions'

    QuestionID = Column(Integer, primary_key=True)
    ExamID = Column(Integer, ForeignKey('Exams.ExamID'))
    QuestionText = Column(Text)
    QuestionType = Column(Enum('MultipleChoice', 'TrueFalse'))

    """Relationships"""
    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question")

    def __init__(self, ExamID, QuestionText, QuestionType):
        self.ExamID = ExamID
        self.QuestionText = QuestionText
        self.QuestionType = QuestionType