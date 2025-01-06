from flask import Flask, render_template, request
import os


# Add path to the project directories
backend_dir = os.path.join(os.getcwd(), 'BackEnd') 
frontend_dir = os.path.join(os.getcwd(), 'FrontEnd')


app = Flask(__name__,
            template_folder=os.path.join(frontend_dir, 'templates'),
            static_folder=os.path.join(frontend_dir, 'static'))

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    print(f"Backend directory: {backend_dir}")
    print(f"Frontend directory: {frontend_dir}")
    app.run(debug=True)