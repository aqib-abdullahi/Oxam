#!/usr/bin/python3
"""initializes models package"""
from models.engine.db_storage import DBstorage

storage = DBstorage()
storage.reload()