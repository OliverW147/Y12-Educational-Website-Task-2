from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import SessionLocal, User, Quiz, Resource, Progress
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'LNeUwX3xj7nteOcybaW59wr5k9faM186'

# Main Page
@app.route('/')
def index():
    return render_template('index.html')

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    db = SessionLocal()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        try:
            new_user = User(username=username, password=password, email=email)
            db.add(new_user)
            db.commit()
            return redirect(url_for('login'))
        except IntegrityError:
            db.rollback()
            flash('Username or email already exists. Please choose a different one.', 'error')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    db = SessionLocal()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.query(User).filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.user_id
            return redirect(url_for('dashboard'))
        flash('Invalid username or password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Dashboard & Resources
@app.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_id=user_id)

@app.route('/resources')
def resources():
    subject = request.args.get('subject', 'Maths')
    topic = request.args.get('topic', 'Algebra')
    # TODO: Implement Resource.getResources method
    # resources = Resource.getResources(subject=subject, topic=topic)
    resources = []  # Placeholdere
    return render_template('resource.html', resources=resources)

# Quiz Views
@app.route('/quiz', methods=['GET', 'POST'])
def take_quiz():
    return render_template('quiz.html')

@app.route('/quiz_results/<int:quiz_id>')
def quiz_results(quiz_id):
    # TODO: Replace with actual query
    quiz = Quiz()  # Placeholder
    return render_template('quiz_results.html', quiz=quiz)

# Progress
@app.route('/progress/<int:user_id>')
def progress(user_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    # TODO: Replace with actual query
    progress = []  # Placeholder
    return render_template('progress.html', progress=progress)

# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Main
if __name__ == '__main__':
    app.run(debug=True)
