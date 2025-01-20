from flask import Flask, render_template, request, redirect, url_for, flash
import os
from models import db, Users, Courses, UserCourses, courses, Lesson, Question, Quizzes, init_data, Contact
from database import init_db
# from database import session
from flask_sqlalchemy import SQLAlchemy 
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # type: ignore
# from flask_wtf import FlaskForm

# Add path to the project directories
backend_dir = os.path.join(os.getcwd(), 'BackEnd') 
frontend_dir = os.path.join(os.getcwd(), 'FrontEnd')


app = Flask(__name__,
            template_folder=os.path.join(frontend_dir, 'templates'),
            static_folder=os.path.join(frontend_dir, 'static'))


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///learning_platform.db'
# app.config['SQLALCHEMY_DATA_URI'] = 'sqlite:///learning_platform.db'
app.config['SECRET_KEY'] = 'your-secret-key'  # For db.session management
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


init_db(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


with app.app_context():
    db.create_all()
    init_data()


@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home/')
def home():
    return render_template('home.html', courses=courses)


@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user and user.check_password(password):
            db.session['username'] = user.username
            db.session['email'] = user.email
            # db.session['password'] = user.password
            flash("Login successful!", "success")
            return redirect('dashboard')
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('login'))
        
    return render_template('login.html')


# Flask-Login 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# logout_user
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')

        if password != password_confirmation:
            flash("Passwords do not match", "error")
            return redirect(url_for('register'))
        
        user = Users.query.filter_by(username=username).first()
        if user:
            flash("Username already exists")
            return redirect(url_for('register'))

        new_user = Users(username=username, email=email, password=password)

        # user = Users(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! ")
        return redirect(url_for('login'))
    
    return render_template('register.html')

# @app.route('/register/', methods=['GET','POST'])
# def register():
    # if request.method == 'POST':
    #     username = request.form.get('username')
    #     email = request.form.get('email')
    #     password = request.form.get('password')
    #     password_confirmation = request.form.get('password_confirmation')

    #     new_user = Users(username=username, email=email, password=password)
    #     db.session.add(new_user)
    #     db.session.commit()
    #     flash("Registration successful! ")
    #     return redirect(url_for('login'))
    
    # return render_template('register.html')

@app.route('/forget_password/')
def forget_password():
    return render_template('forget_password.html')

@app.route('/courses/')
def course_list():
    courses = Courses.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/course_content/<int:course_id>')
@login_required
def course_content(course_id):
    course = Courses.query.get(course_id)
    if not course:
        flash("Course not found!", "error")
        return redirect(url_for('course_list'))
    
    lessons = Lesson.query.filter_by(course_id=course_id).all()
    return render_template('course_content.html', course=course, lessons=lessons)

@app.route('/lesson/<int:course_id>/<int:lesson_id>')
@login_required
def start_lesson(course_id, lesson_id):
    # Ensure the user is enrolled in the course
    course = Courses.query.get(course_id)
    if not course or course not in current_user.courses:
        flash("You are not enrolled in this course.", "error")
        return redirect(url_for('course_list'))

    # Retrieve the lesson
    lesson = Lesson.query.filter_by(course_id=course_id, id=lesson_id).first()
    if not lesson:
        flash("Lesson not found.", "error")
        return redirect(url_for('course_content', course_id=course_id))

    return render_template('lesson.html', lesson=lesson, course=course)

def get_course(course_id):
    return courses.get(course_id)

def get_lesson(course, lesson_id):
    return next((lesson for lesson in course['lessons'] if lesson['id'] == lesson_id), None)


@app.route('/enroll/<int:course_id>',methods=['POST'])
@login_required
def enroll(course_id):
    user = current_user
    # course = Courses.query.get(course_id)
    course = Courses.query.filter_by(id=course_id).first()


    if not course:
        flash("Course not found!", "error")
        return redirect(url_for('course_list'))
    
    if course in user.courses:
        flash("You are already enrolled in this course!", "info")
        return redirect(url_for('course_list'))

    
    user.courses.append(course)
    db.session.commit()
    flash("You have been enrolled in this course!", "success")
    return redirect(url_for('course_list'))


@app.route('/lesson_complete/<int:lesson_id>', methods=['GET'])
@login_required
def lesson_complete(course_id, lesson_id):
    course = Courses.query.get(course_id)
    if not course:
        flash("Course not found!", "error")
        return redirect(url_for('course_list'))
    
    lesson = Lesson.query.filter_by(course_id=course_id, id=lesson_id).first()
    if not lesson:
        flash("Lesson not found!", "error")
        return redirect(url_for('course_content', course_id=course_id))
    
    return render_template('lesson_complete.html', lesson=lesson, course=course)

@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
def quiz(quiz_id):
    quiz = Quizzes.query.get(quiz_id)
    if not quiz:
        flash("Quiz not found!", "error")
        return redirect(url_for('dashboard'))

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not questions:
        flash("No questions available for this quiz!", "error")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f"answers_{question.id}")
            if user_answer and user_answer.strip() == question.answer.strip():
                score += 1

        total_questions = len(questions)
        percentage_score = (score / total_questions) * 100
        feedback = get_feedback(percentage_score, quiz.passing_score)

        return render_template('quiz_feedback.html', quiz=quiz, score=percentage_score, feedback=feedback)

    return render_template('quiz.html', quiz=quiz, questions=questions)


def grade_quiz(quiz, answers):
    questions = Question.query.filter_by(quiz_id=quiz.id).all()
    correct_answers = 0
    total_questions = 0

    for question, answer in zip(questions, answers):
        total_questions += 1
        if answer == question.correct_answer:
            correct_answers += 1
    
    return (correct_answers / total_questions) * 100


def get_feedback(score, passing_score):
    if score >= passing_score:
        return f"Congratulations! You scored {score}% You passed the quiz."
    else:
        return f"Sorry,You scored {score}%. You didn't pass the quiz. Keep trying!"


@app.route('/certificate/')
def certificate():
    return render_template('certificate.html')


@app.route('/user_progress/')
@login_required
def user_progress():
    user = current_user
    enrolled_courses = user.courses
    # progress = {course.id: f"{course.title}: 50% completed" for course in enrolled_courses}
    
    progress = []
    for course in enrolled_courses:
        lessons_completed = get_completed_lessons(user, course)
        quiz_score = get_quiz_score(user, course)
        progress.append({
        "course_id": course.id,
        "course_title": course.title,
        "lessons_completed": lessons_completed,
        "total_lessons": len(course.lessons),
        "quiz_score": quiz_score
        })

    overall_progress = 70  # Example: Overall progress as a percentage
    return render_template('user_progress.html', progress=progress, overall_progress=overall_progress)
    # return render_template('user_progress.html', user=user, courses=enrolled_courses, progress=progress)

@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/contact/')
def contact():
    user = db.session.get('user')
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash("Please fill out all fields!", "error")
            return redirect(url_for('contact'))
        
        new_contact = Contact(name=name, email=email, message=message)
        db.session.add(new_contact)
        db.session.commit()
        flash("Message sent successfully!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')


@app.route('/dashboard/')
@login_required
def dashboard():
    user = current_user
    enrolled_courses = user.courses
    return render_template('dashboard.html', user=user, courses=enrolled_courses)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# @app.route('/courses/')
# def courses():
#     courses = db.session.query(Courses).all()
#     return render_template('courses.html', courses=courses)

# @app.route('/courses/<int:course_id>')
# def course_detail(course_id):
#     course = db.session.query(Courses).get(course_id)
#     return render_template('course_details.html', course=course)

# @app.route('/add_course/')
# def add_course():
#     course_id = request.args.get('course_id')
#     if course_id:
#         course = db.session.query(Courses).get(course_id)
#         return render_template('add_course.html', course=course)
#     else:
#         return render_template('add_course.html')

if __name__ == '__main__':
    # print(f"Backend directory: {backend_dir}")
    # print(f"Frontend directory: {frontend_dir}")
    app.run(debug=True)