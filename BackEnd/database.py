# from models import db, Users, Courses, UserCourses, Lesson, Question, Quizzes
# from sqlalchemy import create_engine 
# from sqlalchemy.orm import sessionmaker 

# DATABASE_URL = "sqlite:///database.db" # path to the database file

# engine = create_engine(DATABASE_URL)
# # BASE.metadata.create_all(engine) # create the table in the database

# # Session is a class
# Session = sessionmaker(bind = engine) 
# # session is an instance of the class Session
# session = Session()
# # create table
# db.metadata.create_all()


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BackEnd.models2 import Base
DATABASE_URL="sqlite:///database.db"
engine=create_engine(DATABASE_URL)
# Drops all tables

Base.metadata.create_all(engine)
Session=sessionmaker(bind=engine)
session=Session()