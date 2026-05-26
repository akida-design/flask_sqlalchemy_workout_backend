from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime

db = SQLAlchemy()

class Exercise(db.Model):
    __tablename__ = 'exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    category = db.Column(db.String(255), nullable=False)
    equipment_needed = db.Column(db.Boolean, default=False)
    
    # Relationship: Exercise has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        backref='exercise',
        cascade='all, delete-orphan',
        foreign_keys='WorkoutExercise.exercise_id'
    )
    
    # Relationship: Exercise has many Workouts through WorkoutExercises
    workouts = db.relationship(
        'Workout',
        secondary='workout_exercises',
        backref='exercises'
    )
    
    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer)
    notes = db.Column(db.Text)
    
    # Relationship: Workout has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        backref='workout',
        cascade='all, delete-orphan',
        foreign_keys='WorkoutExercise.workout_id'
    )
    
    # Relationship: Workout has many Exercises through WorkoutExercises
    # (Already available via backref 'exercises' in Exercise model)
    
    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    
    # Relationships are defined via backref in parent models
    # WorkoutExercise belongs to Workout (backref='workout')
    # WorkoutExercise belongs to Exercise (backref='exercise')
    
    def __repr__(self):
        return f'<WorkoutExercise {self.id}: Workout {self.workout_id}, Exercise {self.exercise_id}>'