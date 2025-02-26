from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Create the base class
Base = declarative_base()


# User
class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    user_type = Column(String(20), nullable=False, default="student")
    registration_date = Column(String(100))

    quizzes = relationship('Quiz', back_populates='user')
    progress = relationship('Progress', back_populates='user')

    def takeQuiz(self, session, quiz_id):
        quiz = session.query(Quiz).filter_by(quiz_id=quiz_id, user_id=self.user_id).first()
        return quiz

    def getProgress(self, session):
        return session.query(Progress).filter_by(user_id=self.user_id).all()

    def updateProfile(self, session, username=None, email=None, password=None):
        if username:
            self.username = username
        if email:
            self.email = email
        if password:
            self.password = password
        session.commit()


# Quiz
class Quiz(Base):
    __tablename__ = 'quizzes'

    quiz_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    topic = Column(String(100), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    quiz_score = Column(Float)

    user = relationship('User', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz')

    def getQuiz(self, session, user_id, topic, difficulty):
        return session.query(Quiz).filter_by(user_id=user_id, topic=topic, difficulty_level=difficulty).first()

    def submitQuiz(self, session, quiz_id, answers):
        quiz = session.query(Quiz).filter_by(quiz_id=quiz_id).first()
        correct_answers = 0
        for i, answer in enumerate(answers):
            question = quiz.questions[i]
            if question.validateAnswer(session, answer):
                correct_answers += 1
        quiz.correct_answers = correct_answers
        quiz.quiz_score = (correct_answers / quiz.total_questions) * 100
        session.commit()


# Question
class Question(Base):
    __tablename__ = 'questions'

    question_id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.quiz_id'))
    question_text = Column(String(300), nullable=False)
    question_type = Column(String(50))
    correct_answer = Column(String(200), nullable=False)
    user_answer = Column(String(200))
    is_correct = Column(Integer)

    quiz = relationship('Quiz', back_populates='questions')

    def validateAnswer(self, session, user_answer):
        self.user_answer = user_answer
        self.is_correct = int(user_answer == self.correct_answer)
        session.commit()
        return self.is_correct

    def getCorrectAnswer(self):
        return self.correct_answer


class Progress(Base):
    __tablename__ = 'progress'

    quiz_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    topic = Column(String(100))
    best_score = Column(Float)

    user = relationship('User', back_populates='progress')

    def updateProgress (self, session, user_id, topic, score):
        progress = session.query(Progress).filter_by(user_id=user_id, topic=topic).first()
        if progress:
            if progress.best_score is None or score > progress.best_score:
                progress.best_score = score
        else:
            # Create a new progress entry
            new_progress = Progress(user_id=user_id, topic=topic, best_score=score)
            session.add(new_progress)
        session.commit()

    def calculateCompletionPercentage(self, session, user_id, subject):
        total_quizzes = session.query(Quiz).filter_by(user_id=user_id, topic=subject).count()
        completed_quizzes = session.query(Progress).filter_by(user_id=user_id, subject=subject).count()
        return (completed_quizzes / total_quizzes) * 100 if total_quizzes > 0 else 0


# Resource
class Resource(Base):
    __tablename__ = 'resources'

    resource_id = Column(Integer, primary_key=True)
    subject = Column(String(100))
    topic = Column(String(100))
    content = Column(String(500))
    resource_type = Column(String(50))
    link = Column(String(200))
    more_links = Column(String(200))

    def getResources(self, session, subject, topic):
        return session.query(Resource).filter_by(subject=subject, topic=topic).all()

# Database
DATABASE_URL = 'sqlite:///site.db'

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
