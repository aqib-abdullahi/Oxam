#!/usr/bin/python3
"""This module defines the user class"""
from models.base import Base
from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.orm import relationship
from flask_login import UserMixin

class User(Base, UserMixin):
    """Defines user by various attributes"""
    __tablename__ = 'Users'

    UserID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(50))
    LastName = Column(String(50))
    # UserName = Column(String(50))
    Email = Column(String(100))
    Password  = Column(String(100))
    Role = Column(Enum('Student', 'Instructor', 'Admin'))
    authenticated = Column(Boolean, default=False)

    """Relationshps"""
    courses = relationship("Course", back_populates="instructor", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="user", cascade="all, delete-orphan")
    registered_courses = relationship("StudentCourse", back_populates="student", cascade="all, delete-orphan")
    question_responses = relationship("QuestionResponse", back_populates="user")  # Add User relationship
    user_studentlog = relationship("Studentlog", back_populates="user")


    def __init__(self, FirstName, LastName, Email, Password, Role, authenticated):
        self.FirstName = FirstName
        self.LastName = LastName
        self.Email = Email
        self.Password = Password
        self.Role = Role
        self.authenticated = authenticated

    def get_id(self):
        return self.Email

    def get_identification(self):
        return  self.UserID


    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def is_active(self):
        return True