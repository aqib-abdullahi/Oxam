#!/usr/bin/python3
"""This module defines the Result class"""
from models.base import Base
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

class Result(Base):
    """Defines it with appropriate attribute"""
    __tablename__ = "Results"

    ResultID = Column(Integer, primary_key=True)
    ExamID = Column(Integer, ForeignKey('Exams.ExamID'))
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    score = Column(Integer)
    Timestamp = Column(DateTime)

    """Relationships"""
    exam = relationship("Exam", back_populates="results")
    user = relationship("User", back_populates="results")

    def __init__(self, ExamID, UserID, score, Timestamp):
        self.ExamID = ExamID
        self.UserID = UserID
        self.score= score
        self.Timestamp = Timestamp