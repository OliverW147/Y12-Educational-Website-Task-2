from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import SessionLocal, User, Quiz, Resource, Progress
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'LNeUwX3xj7nteOcybaW59wr5k9faM186'  # for session management

# Main
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
    db = SessionLocal()
    subject = request.args.get('subject', 'Maths')
    topic = request.args.get('topic', 'Algebra')
    resources = db.query(Resource).filter_by(subject=subject, topic=topic).all()
    return render_template('resource.html', resources=resources)

# Quiz
@app.route('/quiz/<int:quiz_id>', methods=['GET', 'POST'])
def take_quiz(quiz_id):
    db = SessionLocal()
    if request.method == 'POST':
        answers = request.form.getlist('answers')
        quiz = db.query(Quiz).filter_by(quiz_id=quiz_id).first()
        if quiz:
            quiz.submitQuiz(db, quiz_id, answers)  # Pass session as an argument
            # Update the user's progress
            user_id = session.get('user_id')
            if user_id:
                progress = Progress()
                progress.updateProgress(db, user_id, quiz.topic, quiz.quiz_score)
        return redirect(url_for('quiz_results', quiz_id=quiz_id))
    quiz = db.query(Quiz).filter_by(quiz_id=quiz_id).first()
    return render_template('quiz.html', quiz=quiz)

@app.route('/quizzes', methods=['GET', 'POST'])
def quiz():
    return render_template('quiz.html')

@app.route('/quiz_results/<int:quiz_id>')
def quiz_results(quiz_id):
    db = SessionLocal()
    quiz = db.query(Quiz).filter_by(quiz_id=quiz_id).first()
    if quiz:
        return render_template('quiz_results.html', quiz=quiz)
    flash('Quiz not found.', 'error')
    return redirect(url_for('dashboard'))

# Quiz Results
@app.route('/quiz_results')
def all_quiz_results ():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    db = SessionLocal()
    quizzes = db.query(Quiz).filter_by(user_id=user_id).all()
    return render_template('all_quiz_results.html', quizzes=quizzes)

# Error Handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/resources/algebra')
def algebra():
    return render_template('algebra.html')

@app.route('/resources/newton')
def newton():
    return render_template('newton_resource.html')

@app.route('/resources/simultaneous')
def simultaneous():
    return render_template('simultaneous_resource.html')


@app.route('/submit_algebra_quiz', methods=['POST'])
def submit_algebra_quiz():
    db = SessionLocal()
    user_id = session.get('user_id')
    data = request.get_json()
    total_questions = 10

    if user_id and data:
        score = data.get('score')
        quiz_id = data.get('quiz_id')
        topic = 'Algebra'

        try:
            # Fetch or create a quiz entry for the user
            quiz = db.query(Quiz).filter_by(quiz_id=quiz_id, user_id=user_id).first()
            if quiz:
                quiz.correct_answers = score
                quiz.quiz_score = round((score / total_questions) * 100)
            else:
                new_quiz = Quiz(
                    user_id=user_id,
                    topic=topic,
                    difficulty_level='Easy',
                    total_questions=total_questions,
                    correct_answers=score,
                    quiz_score=round((score / total_questions) * 100)
                )
                db.add(new_quiz)

            db.commit()
            # Update user progress
            progress = db.query(Progress).filter_by(user_id=user_id, topic=topic).first()
            if progress:
                if progress.best_score is None or round((score / total_questions) * 100) > progress.best_score:
                    progress.best_score = round((score / total_questions) * 100)

            else:
                new_progress = Progress(user_id=user_id, topic=topic, best_score=round((score / total_questions) * 100))
                db.add(new_progress)

            db.commit()

            return jsonify({'status': 'success', 'message': 'Score saved'})
        except Exception as e:
            db.rollback()
            app.logger.error(f"Error saving quiz: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

@app.route('/progress/<int:user_id>')
def progress(user_id):
    # security
    if session.get('user_id') != user_id:
        return redirect(url_for('login'))

    db = SessionLocal()
    # Fetch the progress entries for the user
    progress_entries = db.query(Progress).filter_by(user_id=user_id).all()
    return render_template('progress.html', progress=progress_entries)

@app.route('/algebra_quiz')
def algebra_quiz():
    return render_template('algebra_quiz.html')

@app.errorhandler(Exception)
def handle_exception(e):
    response = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(response), 500

@app.route('/newtons_laws_quiz')
def newtons_laws_quiz():
    return render_template('newtons_laws_quiz.html')

@app.route('/submit_newtons_laws_quiz', methods=['POST'])
def submit_newtons_laws_quiz():
    db = SessionLocal()
    user_id = session.get('user_id')
    data = request.get_json()
    total_questions = 10

    if user_id and data:
        score = data.get('score')
        quiz_id = data.get('quiz_id')
        topic = 'Newton\'s Laws'

        try:
            # Fetch or create a quiz entry for the user
            quiz = db.query(Quiz).filter_by(quiz_id=quiz_id, user_id=user_id).first()
            if quiz:
                quiz.correct_answers = score
                quiz.quiz_score = round((score / total_questions) * 100)
            else:
                new_quiz = Quiz(
                    user_id=user_id,
                    topic=topic,
                    difficulty_level='Easy',
                    total_questions=total_questions,
                    correct_answers=score,
                    quiz_score=round((score / total_questions) * 100)
                )
                db.add(new_quiz)

            db.commit()
            # Update user progress
            progress = db.query(Progress).filter_by(user_id=user_id, topic=topic).first()
            if progress:
                if progress.best_score is None or round((score / total_questions) * 100) > progress.best_score:
                    progress.best_score = round((score / total_questions) * 100)
            else:
                new_progress = Progress(user_id=user_id, topic=topic, best_score=round((score / total_questions) * 100))
                db.add(new_progress)

            db.commit()

            return jsonify({'status': 'success', 'message': 'Score saved'})
        except Exception as e:
            db.rollback()
            app.logger.error(f"Error saving quiz: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401

@app.route('/simultaneous_equations_quiz')
def simultaneous_equations_quiz():
    # Render the Simultaneous Equations Quiz page
    return render_template('simultaneous_equations_quiz.html')

@app.route('/submit_simultaneous_equations_quiz', methods=['POST'])
def submit_simultaneous_equations_quiz():
    db = SessionLocal()
    user_id = session.get('user_id')
    data = request.get_json()
    total_questions = 10

    if user_id and data:
        score = data.get('score')
        quiz_id = data.get('quiz_id')
        topic = 'Simultaneous Equations'

        try:
            # Fetch or create a quiz entry for the user
            quiz = db.query(Quiz).filter_by(quiz_id=quiz_id, user_id=user_id).first()
            if quiz:
                quiz.correct_answers = score
                quiz.quiz_score = round((score / total_questions) * 100)
            else:
                new_quiz = Quiz(
                    user_id=user_id,
                    topic=topic,
                    difficulty_level='Easy',
                    total_questions=total_questions,
                    correct_answers=score,
                    quiz_score=round((score / total_questions) * 100)
                )
                db.add(new_quiz)

            db.commit()
            # Update user progress
            progress = db.query(Progress).filter_by(user_id=user_id, topic=topic).first()
            if progress:
                if progress.best_score is None or round((score / total_questions) * 100) > progress.best_score:
                    progress.best_score = round((score / total_questions) * 100)
            else:
                new_progress = Progress(user_id=user_id, topic=topic, best_score=round((score / total_questions) * 100))
                db.add(new_progress)

            db.commit()

            return jsonify({'status': 'success', 'message': 'Score saved'})
        except Exception as e:
            db.rollback()
            app.logger.error(f"Error saving quiz: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401


# Main
if __name__ == '__main__':
    app.run(debug=True)
