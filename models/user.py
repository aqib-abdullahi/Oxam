#!/usr/bin/python3
"""This module defines the user class"""
from models.base import Base
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship

class User(Base):
    """Defines user by various attributes"""
    __tablename__ = 'Users'

    UserID = Column(Integer, primary_key=True, autoincrement=True)
    FirstName = Column(String(50))
    LastName = Column(String(50))
    UserName = Column(String(50))
    Email = Column(String(100))
    Password  = Column(String(100))
    Role = Column(Enum('Student', 'Instructor', 'Admin'))

    """Relationshps"""
    courses = relationship("Course", back_populates="instructor")
    results = relationship("Result", back_populates="user")

    def __init__(self, FirstName, LastName, UserName, Email, Password, Role):
        self.FirstName = FirstName
        self.LastName = LastName
        self.UserName = UserName
        self.Email = Email
        self.Password = Password
        self.Role = Role