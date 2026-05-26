from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from datetime import datetime
from sqlalchemy import UniqueConstraint, CheckConstraint

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
        back_populates='exercise',
        cascade='all, delete-orphan',
        foreign_keys='WorkoutExercise.exercise_id'
    )
    
    # Relationship: Exercise has many Workouts through WorkoutExercises
    workouts = db.relationship(
        'Workout',
        secondary='workout_exercises',
        back_populates='exercises',
        overlaps='workout_exercises',
        viewonly=True
    )
    
    @validates('name')
    def validate_name(self, key, value):
        """Validate that exercise name is not empty and has minimum length"""
        if not value or not isinstance(value, str):
            raise ValueError("Exercise name must be a non-empty string")
        if len(value.strip()) < 2:
            raise ValueError("Exercise name must be at least 2 characters long")
        return value.strip()
    
    @validates('category')
    def validate_category(self, key, value):
        """Validate that category is not empty and has minimum length"""
        if not value or not isinstance(value, str):
            raise ValueError("Category must be a non-empty string")
        if len(value.strip()) < 2:
            raise ValueError("Category must be at least 2 characters long")
        return value.strip()
    
    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'
    
    # Table constraint: duration_minutes must be positive (>0)
    __table_args__ = (
        CheckConstraint('duration_minutes > 0', name='check_duration_positive'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    
    # Relationship: Workout has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan',
        foreign_keys='WorkoutExercise.workout_id'
    )
    
    # Relationship: Workout has many Exercises through WorkoutExercises
    exercises = db.relationship(
        'Exercise',
        secondary='workout_exercises',
        back_populates='workouts',
        overlaps='workout_exercises',
        viewonly=True
    )
    
    @validates('date')
    def validate_date(self, key, value):
        """Validate that workout date is not in the future"""
        from datetime import date
        if value > date.today():
            raise ValueError("Workout date cannot be in the future")
        return value
    
    @validates('duration_minutes')
    def validate_duration_minutes(self, key, value):
        """Validate that duration is a positive integer"""
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Duration must be a positive integer")
        return value
    
    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'
    
    # Table constraint: Unique combination of workout and exercise (no duplicates)
    # Table constraint: At least one of reps, sets, or duration_seconds must be provided
    __table_args__ = (
        UniqueConstraint('workout_id', 'exercise_id', name='uq_workout_exercise'),
        CheckConstraint(
            '(reps IS NOT NULL) OR (sets IS NOT NULL) OR (duration_seconds IS NOT NULL)',
            name='check_at_least_one_metric'
        ),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    
    # Relationships using back_populates for clarity
    workout = db.relationship('Workout', back_populates='workout_exercises', overlaps='exercises,workouts')
    exercise = db.relationship('Exercise', back_populates='workout_exercises', overlaps='workouts,exercises')
    
    @validates('reps')
    def validate_reps(self, key, value):
        """Validate that reps is positive if provided"""
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Reps must be a positive integer")
        return value
    
    @validates('sets')
    def validate_sets(self, key, value):
        """Validate that sets is positive if provided"""
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Sets must be a positive integer")
        return value
    
    @validates('duration_seconds')
    def validate_duration_seconds(self, key, value):
        """Validate that duration_seconds is positive if provided"""
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Duration must be a positive integer (in seconds)")
        return value
    
    def __repr__(self):
        return f'<WorkoutExercise {self.id}: Workout {self.workout_id}, Exercise {self.exercise_id}>'