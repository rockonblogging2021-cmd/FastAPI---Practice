from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# SQLite database URL and engine
DATABASE_URL = "sqlite:///./students.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for models
Base = declarative_base()

# Define Student model
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    age = Column(Integer, nullable=False)
    course = Column(String, nullable=False)

# Create all tables and initialize sample data
def initialize_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if db.query(Student).count() == 0:
        students = [
            Student(name="John Doe", age=22, course="Biology"),
            Student(name="Jane Smith", age=21, course="Physics"),
            Student(name="Mike Lee", age=23, course="History"),
            Student(name="Sara Khan", age=22, course="Chemistry"),
            Student(name="Anil Gupta", age=24, course="Mathematics"),
        ]
        db.add_all(students)
        db.commit()
    db.close()

initialize_db()

# Create FastAPI app instance
app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint: Get all students
@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

# Endpoint: Get student by ID
@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
