#!/usr/bin/python3
"""defines the student exam log"""
from models.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, ForeignKey, DateTime

class Studentlog(Base):
    """attributes of the studentlog"""

    __tablename__ = 'Studentlogs'

    StudentlogID = Column(Integer, primary_key=True)
    ExamID = Column(Integer, ForeignKey('Exams.ExamID'))
    UserID = Column(Integer, ForeignKey('Users.UserID'))
    ExamStartedAt = Column(DateTime)

    """relationships"""
    exam = relationship("Exam", back_populates="exam_started")
    user = relationship("User", back_populates="user_studentlog")

    def __init__(self, ExamID, ExamStartedAt, UserID):
        self.ExamID = ExamID
        self.ExamStartedAt = ExamStartedAt
        self.UserID = UserID