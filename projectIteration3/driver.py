from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Quiz, Progress
DATABASE_URL = 'sqlite:///:memory:'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)
session = SessionLocal()
user = User(username='user', password='pass', email='testuser@example.com')
session.add(user)
session.commit()

# Test invalid email
try:
    user.updateProfile(session, email='invalid-email')
    assert False, "Expected exception for invalid email format."
except Exception:
    pass

# fetching quiz with no matching criteria
result = Quiz().getQuiz(session, user_id=user.user_id, topic='Science', difficulty='Hard')
assert result is None, "Expected None when no matching quiz exists."

# updating progress when no progress exists
progress = Progress()
progress.updateProgress(session, user_id=user.user_id, topic='Math', score=80.0)
result = session.query(Progress).filter_by(user_id=user.user_id, topic='Math').first()
assert result is not None, "Expected a new progress entry."
assert result.best_score == 80.0, "Expected best_score to be updated to 80.0."

session.rollback()
session.close()
print("Done.")
