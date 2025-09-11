"""
Database package for AI Marketing Automation Platform
"""
from database.models import *
from database.connection import get_db, engine, SessionLocal, init_db, check_db_connection, DatabaseManager
from database.crud import *