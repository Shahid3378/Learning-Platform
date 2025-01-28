from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime, LargeBinary
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# User Model
class Users(Base):
    _tablename_ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    role = Column(String(100))
    password = Column(String(100), nullable=False)
    progress = relationship('UserProgress', back_populates='user', cascade="all, delete-orphan")
    enrollments = relationship('Enrollment', back_populates='user', cascade="all, delete-orphan")
    answers = relationship('UserAnswer', back_populates='user', cascade="all, delete-orphan")

# Course Model
class Courses(Base):
    _tablename_ = 'courses'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(500))
    course_thumbnail = Column(LargeBinary, nullable=True)
    lessons = relationship('Lesson', back_populates='course', cascade="all, delete-orphan")
    quizzes = relationship('Quiz', back_populates='course', cascade="all, delete-orphan")
    progress = relationship('UserProgress', back_populates='course', cascade="all, delete-orphan")
    enrollments = relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")

# Lesson Model
class Lesson(Base):
    _tablename_ = 'lessons'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(200), nullable=False)
    completed = Column(Boolean, default=False)
    course_link = Column(String(500), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id', ondelete='CASCADE'))
    course = relationship('Course', back_populates='lessons')