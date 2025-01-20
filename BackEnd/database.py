from models import db, Users, Courses, UserCourses, Lesson, Question, Quizzes , init_data
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker 

DATABASE_URL = "sqlite:///learning_platform.db" # path to the database file

engine = create_engine(DATABASE_URL)
# BASE.metadata.create_all(engine) # create the table in the database

# Session is a class
Session = sessionmaker(bind = engine) 
# session is an instance of the class Session
session = Session()

def init_db(app):
    # Bind the Flask app to SQLAlchemy
    db.init_app(app)
    
    # Create tables in the database
    with app.app_context():
        db.create_all()
        
        # Populate the database with initial data
        init_data()
