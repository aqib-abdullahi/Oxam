#!/usr/bin/python3
"""This module defines the Answer class"""
from models.base import Base
from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

class Answer(Base):
    """Defines it with appropriate attriutes"""
    __tablename__ = "Answers"

    AnswerID = Column(Integer, primary_key=True)
    QuestionID = Column(Integer, ForeignKey("Questions.QuestionID"))
    AnswerText = Column(Text)
    CorrectAnswer = Column(Text)

    """Relationships"""
    question = relationship("Question", back_populates="answers")

    def __init__(self, QuestionID, AnswerText, CorrectAnswer):
        self.QuestionID = QuestionID
        self.AnswerText = AnswerText
        self.CorrectAnswer = CorrectAnswer