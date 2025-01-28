from flask import Flask, render_template, request, redirect, url_for, flash
import os
# from flask import session
from flask_login import LoginManager, login_required, current_user, login_user, logout_user, UserMixin # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash   # type: ignore
# from models import db, Users, Courses, UserCourses, Lesson, Question, Quizzes, Contact, bcrypt, UserLessonProgress, QuizResult , courses
from flask_migrate import Migrate
from BackEnd.models2 import Course
from database import session as db_session
from models import Courses, Users, Lesson

# Add path to the project directories
backend_dir = os.path.join(os.getcwd(), 'BackEnd') 
frontend_dir = os.path.join(os.getcwd(), 'FrontEnd')

app = Flask(__name__,
            template_folder=os.path.join(frontend_dir, 'templates'),
            static_folder=os.path.join(frontend_dir, 'static'))

# For db.session management
app.config['SECRET_KEY'] = '9224ab35a0fb246961b5d55a' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ums.sqlite'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db.init_app(app) # Link sqlalchemy with the app
# Sesson(app)
# migrate = Migrate(app, db)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'


# db.init_app(app)
# bcrypt.init_app(app)

# with app.app_context():
#     add_courses_to_db()
#     init_data()


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home/')
def home():
    courses = Courses.query.all()
    return render_template('home.html', courses=courses)

@app.route('/admin/add_course/', methods=['POST'])
def add_course():
    # Ensure the user is an admin
    # if 'username' not in session or session.get('role') != 'admin':
    #     return redirect(url_for('get_login'))
    
    if request.method == 'POST':
        # Manually specify the course data (you can replace these values)
        title = "Python for Beginners"
        description = "A comprehensive introduction to Python programming."
        
        # For course thumbnail, we would normally need a file, 
        # so here we simulate it by reading an image file if needed.
        with open("path_to_thumbnail.jpg", "rb") as file:
            course_thumbnail = file.read()

        # Define the lessons data manually
        lessons_data = [
            {
                'title': 'Introduction to Python',
                'content': 'This lesson introduces the basic concepts of Python.',
                'course_link': 'https://example.com/python_intro'
            },
            {
                'title': 'Variables and Data Types',
                'content': 'Learn about Python variables and data types.',
                'course_link': 'https://example.com/variables_data_types'
            }
        ]
        
        # Create the new course object and add it to the database
        new_course = Course(title=title, description=description, course_thumbnail=course_thumbnail)
        db_session.add(new_course)
        db_session.commit()

        # Add lessons for the newly created course
        for lesson in lessons_data:
            new_lesson = Lesson(
                title=lesson['title'],
                content=lesson['content'],
                course_link=lesson['course_link'],
                course_id=new_course.id
            )
            db_session.add(new_lesson)

        db_session.commit()
        print("Courses and lessons added successfully.")
        return jsonify({"message": "Course and lessons added successfully."}), 201

@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('login'))
        
    return render_template('login.html')


# logout_user
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/')
def profile():
    return f"Welcome {current_user.username}, you are logged in as {current_user.role}!"

# Flask-Login 
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')

        if password != password_confirmation:
            flash("Passwords do not match", "error")
            return render_template('register.html', username=username,email=email)
        
        if Users.query.filter_by(username=username).first():
            flash("Username already exists", "error")
            return render_template('register.html',email=email)
        if Users.query.filter_by(email=email).first():
            flash("Email already exists","error")
            return render_template('register.html',username=username)
        
        role = request.form.get('role', 'user')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = Users(fname=fname, lname=lname,username=username, email=email, password=hashed_password, role=role)

        # user = Users(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("User Registration Successful! ")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/forget_password/')
def forget_password():
    return render_template('forget_password.html')

@app.route('/courses/')
def course_list():
    courses = Courses.query.all()
    # print(courses)
    return render_template('courses.html', courses=courses)

@app.route('/course_content/<int:course_id>')
# @login_required
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

def get_completed_lessons(user_id):
    return Lesson.query.join(UserLessonProgress).filter(
        UserLessonProgress.user_id == user_id, 
        UserLessonProgress.completed == True
    ).all()

def get_quiz_score(user_id, quiz_id):
    return QuizResult.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()

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
    for lesson in course.lessons:
        progress = UserLessonProgress(user_id=user.id, lesson_id=lesson.id, lesson_completed=False)
        db.session.add(progress)
    db.session.commit()
    flash("You have been enrolled in this course!", "success")
    return redirect(url_for('course_list'))

@app.route('/user_courses/')
def user_courses():
    user = Users.query.get(1)  # Get a user with ID 1
    if user:
        courses = user.courses  # Access the courses the user is enrolled in
        return render_template('user_courses.html', user=user, courses=courses)
    return "User not found", 404

@app.route('/lesson_complete/<int:course_id>/<int:lesson_id>/', methods=['GET'])
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
    
    progress = UserLessonProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    if progress:
        progress.lesson_completed = True  # Mark the lesson as completed
        db.session.commit()

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
        return redirect(url_for('user_dashboard'))

    if request.method == 'POST':
        score = 0
        for question in questions:
            user_answer = request.form.get(f"answers_{question.id}")
            if user_answer and user_answer.strip() == question.answer.strip():
                score += 1

        total_questions = len(questions)
        percentage_score = (score / total_questions) * 100
        feedback = get_feedback(percentage_score, quiz.passing_score)

        quiz_result = QuizResult.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()
        if not quiz_result:
            quiz_result = QuizResult(user_id=current_user.id, quiz_id=quiz.id)
            db.session.add(quiz_result)

        quiz_result.score = percentage_score
        quiz_result.passed = percentage_score >= quiz.passing_score
        db.session.commit()

        print(f"Score: {score} out of {total_questions}")
        print(f"Percentage: {percentage_score}%")
        
        return render_template('quiz_feedback.html', quiz=quiz, score=percentage_score, feedback=feedback)

    return render_template('quiz.html', quiz=quiz, questions=questions)


def get_completed_lessons(user):
    return Lesson.query.join(UserLessonProgress).filter(
        UserLessonProgress.user_id == user.id, 
        UserLessonProgress.lesson_completed == True
    ).all()

def get_completed_courses(user):
    return Courses.query.join(UserCourses).filter(
        UserCourses.user_id == user.id
    ).all()

def get_quiz_score(user, quiz_id):
    quiz_result = QuizResult.query.filter_by(user_id=user.id, quiz_id=quiz_id).first()
    return quiz_result.score if quiz_result else None


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


# @app.before_first_request
# def setup_courses():
#     add_courses()

@app.route('/add_courses')
def add_courses_view():
    add_courses()  # Populate the database with courses and lessons
    return 'Courses added successfully!'

def add_courses(course):
    courses = [
        {'id': 1, 'title': 'HTML & CSS', 'description': 'Learn the fundamentals of web development with HTML and CSS.', 
        'image': 'html_css_icon.jpeg',
        'lessons': [
            {'id': 1, 'title': 'Introduction to HTML & CSS', 'description': 'Learn the basics of HTML and CSS.'},
            {'id': 2, 'title': 'CSS Basics', 'description': 'Learn how to style your web pages with CSS.'}
        ]},
        
        {'id': 2, 'title': 'JavaScript', 'description': 'Dive into JavaScript for dynamic web content.', 
        'image': 'js_icon.jpeg',
        'lessons': [
            {'id': 1, 'title': 'Introduction to JavaScript', 'description': 'Get started with JavaScript.'},
            {'id': 2, 'title': 'JavaScript Functions', 'description': 'Learn about functions in JavaScript.'}
        ]},
        
        {'id': 3, 'title': 'Python', 'description': 'Master Python programming.', 
        'image': 'python_icon.jpeg',
        'lessons': [
            {'id': 1, 'title': 'Introduction to Python', 'description': 'Learn the basics of Python.'},
            {'id': 2, 'title': 'Python Functions', 'description': 'Learn how to create functions in Python.'}
        ]}
    ]
    
    try:
        for course_data in courses:
            # Check if the course already exists in the database
            existing_course = Courses.query.filter_by(title=course_data['title']).first()
            
            # If the course doesn't exist, add it
            if not existing_course:
                course = Courses(
                    title=course_data['title'],
                    description=course_data['description'],
                    image=course_data['image']
                )
                db.session.add(course)
                db.session.commit()  # Commit after adding the course
                
                # After adding the course, add lessons to it
                for lesson_data in course_data['lessons']:
                    lesson = Lesson(
                        title=lesson_data['title'],
                        description=lesson_data['description'],
                        course_id=course.id 
                    )
                    db.session.add(lesson)
                
                db.session.commit()  # Commit after adding the lessons
    except Exception as e:
        db.session.rollback()
        print(f"Error occurred while committing courses: {e}")

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
    if  current_user.is_authenticated:
        user = db.session.get(Users, current_user.id)

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

#  Admin

@app.route('/admin/manage_courses/')
def admin_manage_courses():
    return render_template('admin_manage_courses.html')


@app.route('/admin/manage_users/')
def admin_manage_users():
    return render_template('admin_manage_users.html')

@app.route('/admin/reports/')
def admin_reports():
    return render_template('admin_reports.html')


@app.route('/admin/dashboard/')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')
    
@app.route('/user/dashboard/')
@login_required
def user_dashboard():
    # if Sesson.get('username'):
        # return render_template('user_dashboard.html')
    user_courses = UserCourses.query.filter_by(user_id=current_user.id).all()
    courses = [user_course.course for user_course in user_courses]  # Extract courses
    return render_template('user_dashboard.html', courses=courses)



def create_quizzes():
    # Check if quizzes already exist
    if not Quizzes.query.first():
        # Create quizzes for each course
        html_css_quiz = Quizzes(title="HTML & CSS Basics Quiz", passing_score=80, course_id=1)
        js_quiz = Quizzes(title="JavaScript Basics Quiz", passing_score=80, course_id=2)
        python_quiz = Quizzes(title="Python Basics Quiz", passing_score=80, course_id=3)

        db.session.add_all([html_css_quiz, js_quiz, python_quiz])
        db.session.commit()

        create_questions(html_css_quiz.id, js_quiz.id, python_quiz.id)


def create_questions(html_css_quiz_id, js_quiz_id, python_quiz_id):
    
        # Create questions for HTML & CSS quiz
        html_css_quiz = [
            {"question": "What does HTML stand for?", 
            "option_A": "HyperText Markup Language", 
            "option_B": "Hyperlink Text Markup Language", 
            "option_C": "Home Tool Markup Language", 
            "option_D": "None of the above", 
            "answer": "HyperText Markup Language"
            },
            {"question": "Which HTML element is used to define the title of a web page?",
            "option_A": "<h1>", 
            "option_B": "<title>", 
            "option_C": "<head>", 
            "option_D": "<body>", 
            "answer": "<title>"
            },
            {"question": "Which of the following is the correct syntax for linking an external CSS file?", 
            "option_A": "<style src='style.css'>", 
            "option_B": "<link rel='stylesheet' href='style.css'>", "option_C": "<css src='style.css'>", 
            "option_D": "<link href='style.css'>", 
            "answer": "<link rel='stylesheet' href='style.css'>"
            },
            {"question": "How do you make a list in HTML?", 
            "option_A": "<list>", 
            "option_B": "<ul>", 
            "option_C": "<ol>", 
            "option_D": "<dl>", 
            "answer": "<ul>"
            },
            {"question": "Which CSS property is used to change the background color of an element?", 
            "option_A": "bgcolor", 
            "option_B": "background-color", 
            "option_C": "color", 
            "option_D": "background", 
            "answer": "background-color"
            },
            {"question": "Which tag is used to create a hyperlink in HTML?", 
            "option_A": "<a>", 
            "option_B": "<link>", 
            "option_C": "<url>", 
            "option_D": "<hyperlink>", 
            "answer": "<a>"
            },
            {"question": "What is the correct syntax for adding a comment in CSS?", 
            "option_A": "// comment", 
            "option_B": "/* comment */", 
            "option_C": "<!-- comment -->", 
            "option_D": "# comment", 
            "answer": "/* comment */"
            },
            {"question": "Which property is used to change the text color in CSS?", 
            "option_A": "font-color", 
            "option_B": "color", 
            "option_C": "text-color", 
            "option_D": "text-style", "answer": "color"
            },
            {"question": "What does the <div> tag represent in HTML?", "option_A": "A division or section in a document", "option_B": "A paragraph of text", 
            "option_C": "An image container", 
            "option_D": "A table row", 
            "answer": "A division or section in a document"
            },
            {"question": "How do you add a background image in CSS?", "option_A": "background-image: url('image.jpg');", "option_B": "image: url('image.jpg');", "option_C": "background: 'image.jpg';", "option_D": "image-background: url('image.jpg');", 
            "answer": "background-image: url('image.jpg');"
            }
        ]

        # Create questions for JavaScript quiz
        js_quiz = [
            {"question": "What is the correct way to define a variable in JavaScript?", 
            "option_A": "var x = 5;", 
            "option_B": "variable x = 5;", 
            "option_C": "define x = 5;", 
            "option_D": "x = 5;", 
            "answer": "var x = 5;"
            },
            {"question": "Which method is used to display an alert box in JavaScript?", 
            "option_A": "alert()", 
            "option_B": "popup()", 
            "option_C": "msg()", 
            "option_D": "show()", 
            "answer": "alert()"
            },
            {"question": "How do you create a function in JavaScript?", "option_A": "function myFunction() { }", 
            "option_B": "func myFunction() { }", 
            "option_C": "function: myFunction() { }", 
            "option_D": "create function myFunction() { }", 
            "answer": "function myFunction() { }"
            },
            {"question": "Which of the following is NOT a valid JavaScript data type?", 
            "option_A": "String", 
            "option_B": "Integer", 
            "option_C": "Boolean", 
            "option_D": "Undefined", 
            "answer": "Integer"
            },
            {"question": "How do you add a comment in JavaScript?", "option_A": "<!-- This is a comment -->", 
            "option_B": "// This is a comment", 
            "option_C": "/* This is a comment */", 
            "option_D": "# This is a comment", 
            "answer": "// This is a comment"
            },
            {"question": "What is the correct syntax to call a function named 'myFunction'?", "option_A": "call myFunction()", "option_B": "myFunction();", "option_C": "invoke myFunction()", "option_D": "execute myFunction()", "answer": "myFunction();"},
            {"question": "Which of these is the correct way to declare an array in JavaScript?", 
            "option_A": "let arr = [1, 2, 3];", 
            "option_B": "let arr = (1, 2, 3);", 
            "option_C": "let arr = {1, 2, 3};", 
            "option_D": "let arr = 1, 2, 3;", 
            "answer": "let arr = [1, 2, 3];"
            },
            {"question": "Which JavaScript method is used to find the length of an array?", 
            "option_A": "length()", 
            "option_B": "size()", 
            "option_C": "arrayLength()", 
            "option_D": ".length", 
            "answer": ".length"
            },
            {"question": "Which of the following loops is used to execute a block of code while a condition is true?", "option_A": "for", 
            "option_B": "while", 
            "option_C": "do-while", 
            "option_D": "All of the above", 
            "answer": "All of the above"
            },
            {"question": "What is the result of '5' + 5 in JavaScript?", "option_A": "'55'", 
            "option_B": "10", 
            "option_C": "Error", 
            "option_D": "'5' + '5'", 
            "answer": "'55'"
            }
        ]

        # Create questions for Python quiz
        python_quiz = [
            {"question": "What is the correct syntax to print 'Hello, World!' in Python?", 
            "option_A": "echo 'Hello, World!'", 
            "option_B": "print('Hello, World!')", 
            "option_C": "console.log('Hello, World!')", 
            "option_D": "print(Hello, World!)", 
            "answer": "print('Hello, World!')"
            },
            {"question": "Which of the following is a Python data type?", 
            "option_A": "Integer", 
            "option_B": "Boolean", 
            "option_C": "List", 
            "option_D": "All of the above", 
            "answer": "All of the above"
            },
            {"question": "How do you define a function in Python?", "option_A": "function myFunction():", 
            "option_B": "def myFunction():", 
            "option_C": "func myFunction():", 
            "option_D": "function: myFunction()", 
            "answer": "def myFunction():"
            },
            {"question": "Which of the following is the correct way to create a list in Python?", 
            "option_A": "list = (1, 2, 3)", 
            "option_B": "list = [1, 2, 3]", 
            "option_C": "list = {1, 2, 3}", 
            "option_D": "list = <1, 2, 3>", 
            "answer": "list = [1, 2, 3]"
            },
            {"question": "How do you add an item to a list in Python?", "option_A": "list.add(4)", "option_B": "list.append(4)", "option_C": "list.insert(4)", "option_D": "list.push(4)", "answer": "list.append(4)"},
            {"question": "Which of the following is used to handle errors in Python?", 
            "option_A": "try...catch", 
            "option_B": "try...except", 
            "option_C": "catch...finally", 
            "option_D": "throw...catch", 
            "answer": "try...except"
            },
            {"question": "What is the result of '3 == 3' in Python?", "option_A": "True", 
            "option_B": "False", 
            "option_C": "Error", 
            "option_D": "None", 
            "answer": "True"
            },
            {"question": "Which Python operator is used for exponentiation?", 
            "option_A": "^", 
            "option_B": "**", 
            "option_C": "*", 
            "option_D": "++", 
            "answer": "**"
            },
            {"question": "What is the correct syntax to comment a single line in Python?", 
            "option_A": "<!-- This is a comment -->", 
            "option_B": "# This is a comment", 
            "option_C": "/* This is a comment */", 
            "option_D": "// This is a comment", 
            "answer": "# This is a comment"
            },
            {"question": "Which function is used to get the length of a list in Python?", "option_A": "list.size()", "option_B": "list.length()", "option_C": "len(list)", "option_D": "list.length", "answer": "len(list)"
            }
        ]

        for q in html_css_quiz:
            db.session.add(Question(**q, quiz_id=html_css_quiz.id))
        
        for q in js_quiz:
            db.session.add(Question(**q, quiz_id=js_quiz.id))
        
        for q in python_quiz:
            db.session.add(Question(**q, quiz_id=python_quiz.id))
        
        db.session.commit()



def create_courses():
    """Create courses if they don't already exist."""
    if not Courses.query.first():
        html_css_course = Courses(title="HTML & CSS", description="Learn the fundamentals of web development with HTML and CSS.")
        js_course = Courses(title="JavaScript", description="Dive into JavaScript for dynamic web content.")
        python_course = Courses(title="Python", description="Master Python programming.")

        db.session.add_all([html_css_course, js_course, python_course])
        db.session.commit()

        print("Courses created successfully!")

    return Courses.query.all()


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


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