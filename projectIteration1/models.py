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
    user_type = Column(String(20), nullable=False, default="student")  # E.g., student, teacher
    registration_date = Column(String(100))

    # Relationships
    quizzes = relationship('Quiz', back_populates='user')
    progress = relationship('Progress', back_populates='user')

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"


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

    # Relationships
    user = relationship('User', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz')

    def __repr__(self):
        return f"<Quiz(topic={self.topic}, score={self.quiz_score})>"


# Question
class Question(Base):
    __tablename__ = 'questions'

    question_id = Column(Integer, primary_key=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.quiz_id'))
    question_text = Column(String(300), nullable=False)
    question_type = Column(String(50))  # E.g., multiple choice, true/false, etc.
    correct_answer = Column(String(200), nullable=False)
    user_answer = Column(String(200))
    is_correct = Column(Integer)

    # Relationships
    quiz = relationship('Quiz', back_populates='questions')

    def __repr__(self):
        return f"<Question(question_text={self.question_text})>"


# Progress
class Progress(Base):
    __tablename__ = 'progress'

    progress_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    subject = Column(String(100))
    topic = Column(String(100))
    quiz_avg_score = Column(Float)
    completion_percentage = Column(Float)
    weak_areas = Column(String(500))

    # Relationships
    user = relationship('User', back_populates='progress')

    def __repr__(self):
        return f"<Progress(subject={self.subject}, topic={self.topic})>"


# Resource
class Resource(Base):
    __tablename__ = 'resources'

    resource_id = Column(Integer, primary_key=True)
    subject = Column(String(100))
    topic = Column(String(100))
    content = Column(String(500))
    resource_type = Column(String(50))
    # getResource method here

    def __repr__(self):
        return f"<Resource(subject={self.subject}, topic={self.topic})>"

# Database
DATABASE_URL = 'sqlite:///site.db'

# Create engine
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
