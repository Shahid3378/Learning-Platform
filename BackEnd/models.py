from sqlalchemy import Column, Integer, String  # create_engine, 
# from sqlalchemy.ext.declarative import declarative_db
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin 
import bcrypt 

db = SQLAlchemy()

# Data for Courses

courses = {
    1: {'title': 'HTML & CSS', 'description': 'Learn the fundamentals of web development with HTML and CSS.', 
        'image': 'html_css_icon.jpeg',
    'lessons': [
        {'id': 1, 'title': 'Introduction to HTML & CSS', 'description': 'Learn the basics of HTML and CSS.'},
        {'id': 2, 'title': 'CSS Basics', 'description': 'Learn how to style your web pages with CSS.'}
    ]},
    2: {'title': 'JavaScript', 'description': 'Dive into JavaScript for dynamic web content.', 
    'image': 'js_icon.jpeg',
    'lessons': [
        {'id': 1, 'title': 'Introduction to JavaScript', 'description': 'Get started with JavaScript.'},
        {'id': 2, 'title': 'JavaScript Functions', 'description': 'Learn about functions in JavaScript.'}
    ]},
    3: {'title': 'Python', 'description': 'Master Python programming.', 
        'image': 'python_icon.jpeg',
        'lessons': [
        {'id': 1, 'title': 'Introduction to Python', 'description': 'Learn the basics of Python.'},
        {'id': 2, 'title': 'Python Functions', 'description': 'Learn how to create functions in Python.'}
    ]}
}


# Users model
class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    fname = db.Column(String(255), nullable=False)
    lname = db.Column(String(255), nullable=False)
    username = db.Column(String(255),unique=True, nullable=False)
    email = db.Column(String(255),unique=True, nullable=False)
    password = db.Column(String(255), nullable=False)
    courses = db.relationship('Courses', secondary='user_courses', back_populates='students', lazy=True)

    def __init__(self, fname, lname, username, email, password):
        self.fname = fname
        self.lname = lname
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

# UserCourses model
class UserCourses(db.Model):
    __tablename__ = 'user_courses'
    user_id = db.Column(Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(Integer, db.ForeignKey('courses.id'), primary_key=True)


# Courses model
class Courses(db.Model):
    __tablename__ = 'courses'
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    description = db.Column(String(255), nullable=False)
    students = db.relationship('Users', secondary='user_courses', back_populates='courses', lazy=True)
    lessons = db.relationship('Lesson', backref='course', lazy=True)
    quizzes = db.relationship('Quizzes', backref='course', lazy=True)


# Lesson model 
class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    description = db.Column(String(255), nullable=False)
    course_id = db.Column(Integer, db.ForeignKey('courses.id'), nullable=False)

# Quiz model 
class Quizzes(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(255), nullable=False)
    passing_score = db.Column(Integer, nullable=False, default=50)
    course_id = db.Column(Integer, db.ForeignKey('courses.id') , nullable=False)

    questions = db.relationship('Question', backref='quiz', lazy=True)


class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(Integer, primary_key=True)
    question = db.Column(String(255), nullable=False)
    option = db.Column(String(255), nullable=False)
    answer = db.Column(String(255), nullable=False)

    quiz_id = db.Column(Integer, db.ForeignKey('quizzes.id'), nullable=False)


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    message = db.Column(db.Text, nullable=False)
    

def init_data():
    # Create courses
    if not Courses.query.first():
        html_css_course = Courses(title="HTML & CSS", description="Learn the fundamentals of web development with HTML and CSS.")
        js_course = Courses(title="JavaScript", description="Dive into JavaScript for dynamic web content.")
        python_course = Courses(title="Python", description="Master Python programming.")
    
        db.session.add_all([html_css_course, js_course, python_course])
        db.session.commit()

        # Create lessons for HTML & CSS
        lesson1 = Lesson(title="Introduction to HTML & CSS", description="Learn the basics of HTML and CSS.", course_id=html_css_course.id)
        lesson2 = Lesson(title="CSS Basics", description="Learn how to style your web pages with CSS.", course_id=html_css_course.id)

        # Create lessons for JavaScript
        lesson3 = Lesson(title="Introduction to JavaScript", description="Get started with JavaScript.", course_id=js_course.id)
        lesson4 = Lesson(title="JavaScript Functions", description="Learn about functions in JavaScript.", course_id=js_course.id)

        # Create lessons for Python
        lesson5 = Lesson(title="Introduction to Python", description="Learn the basics of Python.", course_id=python_course.id)
        lesson6 = Lesson(title="Python Functions", description="Learn how to create functions in Python.", course_id=python_course.id)

        db.session.add_all([lesson1, lesson2, lesson3, lesson4, lesson5, lesson6])
        db.session.commit()

        # Create quizzes for HTML & CSS
        html_css_quiz = Quizzes(title="HTML & CSS Basics Quiz", passing_score=80, course_id=html_css_course.id)
        js_quiz = Quizzes(title="JavaScript Basics Quiz", passing_score=80, course_id=js_course.id)
        python_quiz = Quizzes(title="Python Basics Quiz", passing_score=80, course_id=python_course.id)

        db.session.add_all([html_css_quiz, js_quiz, python_quiz])
        db.session.commit()

        # Create questions for HTML & CSS quiz
        q1 = Question(
        question="What does HTML stand for?",  # Updated "question_text" to "question"
        option="HyperText Markup Language, HighText Markup Language",
        answer="HyperText Markup Language",
        quiz_id=html_css_quiz.id
        )
        q2 = Question(
        question="What is the purpose of CSS?",  # Updated "question_text" to "question"
        option="To style HTML elements, To create HTML documents",
        answer="To style HTML elements",
        quiz_id=html_css_quiz.id
        )

        # Create questions for JavaScript quiz
        q3 = Question(
        question="What does JavaScript do?",  # Updated "question_text" to "question"
        option="Adds interactivity to the web, Formats text",
        answer="Adds interactivity to the web",
        quiz_id=js_quiz.id
        )
        q4 = Question(
        question="Which of the following is a JavaScript data type?",  # Updated "question_text" to "question"
        option="String, Integer, Real",
        answer="String",
        quiz_id=js_quiz.id
        )

        # Create questions for Python quiz
        q5 = Question(
        question="What is Python?",  # Updated "question_text" to "question"
        option="A programming language, A fruit",
        answer="A programming language",
        quiz_id=python_quiz.id
        )
        q6 = Question(
        question="What is the purpose of a Python function?",  # Updated "question_text" to "question"
        option="To repeat code, To define reusable blocks of code",
        answer="To define reusable blocks of code",
        quiz_id=python_quiz.id
        )

        db.session.add_all([q1, q2, q3, q4, q5, q6])
        db.session.commit()
