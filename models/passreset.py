#!/usr/bin/python3
"""password reset module"""
from models.base import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class PasswordResetToken(Base):
    __tablename__ = 'password_reset_tokens'

    ResetID = Column(Integer, primary_key=True)
    UserID = Column(Integer, ForeignKey('Users.UserID'), nullable=False)
    Token = Column(String(255), nullable=False, unique=True)
    ExpiresAt = Column(DateTime, nullable=False)

    """Relationship"""
    userpass = relationship('User', back_populates='reset_tokens')

    def __init__(self, Token, ExpiresAt, UserID):
        self.Token = Token
        self.ExpiresAt = ExpiresAt
        self.UserID = UserID