#!/usr/bin/env python3

from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date, timedelta

with app.app_context():
    # Clear existing data
    print(" Clearing existing data...")
    db.drop_all()
    db.create_all()
    
    # Create Exercises
    print(" Creating exercises...")
    exercises = [
        Exercise(name='Push-ups', category='Chest', equipment_needed=False),
        Exercise(name='Squats', category='Legs', equipment_needed=False),
        Exercise(name='Bench Press', category='Chest', equipment_needed=True),
        Exercise(name='Deadlifts', category='Back', equipment_needed=True),
        Exercise(name='Pull-ups', category='Back', equipment_needed=False),
        Exercise(name='Lunges', category='Legs', equipment_needed=False),
        Exercise(name='Plank', category='Core', equipment_needed=False),
        Exercise(name='Barbell Rows', category='Back', equipment_needed=True),
    ]
    db.session.add_all(exercises)
    db.session.commit()
    
    # Create Workouts
    print("  Creating workouts...")
    today = date.today()
    workouts = [
        Workout(
            date=today - timedelta(days=2),
            duration_minutes=45,
            notes='Upper body strength training - heavy focus on chest and back'
        ),
        Workout(
            date=today - timedelta(days=1),
            duration_minutes=60,
            notes='Lower body and core - high intensity'
        ),
        Workout(
            date=today,
            duration_minutes=50,
            notes='Full body compound movements'
        ),
    ]
    db.session.add_all(workouts)
    db.session.commit()
    
    # Create WorkoutExercises (join table records)
    print(" Creating workout exercises...")
    workout_exercises = [
        # Workout 1 (2 days ago): Upper body
        WorkoutExercise(
            workout_id=workouts[0].id,
            exercise_id=exercises[2].id,  # Bench Press
            reps=8,
            sets=4,
            duration_seconds=None
        ),
        WorkoutExercise(
            workout_id=workouts[0].id,
            exercise_id=exercises[0].id,  # Push-ups
            reps=15,
            sets=3,
            duration_seconds=None
        ),
        WorkoutExercise(
            workout_id=workouts[0].id,
            exercise_id=exercises[4].id,  # Pull-ups
            reps=10,
            sets=3,
            duration_seconds=None
        ),
        # Workout 2 (1 day ago): Lower body
        WorkoutExercise(
            workout_id=workouts[1].id,
            exercise_id=exercises[1].id,  # Squats
            reps=12,
            sets=4,
            duration_seconds=None
        ),
        WorkoutExercise(
            workout_id=workouts[1].id,
            exercise_id=exercises[3].id,  # Deadlifts
            reps=5,
            sets=5,
            duration_seconds=None
        ),
        WorkoutExercise(
            workout_id=workouts[1].id,
            exercise_id=exercises[5].id,  # Lunges
            reps=10,
            sets=3,
            duration_seconds=None
        ),
        # Workout 3 (today): Full body
        WorkoutExercise(
            workout_id=workouts[2].id,
            exercise_id=exercises[2].id,  # Bench Press
            reps=6,
            sets=3,
            duration_seconds=None
        ),
        WorkoutExercise(
            workout_id=workouts[2].id,
            exercise_id=exercises[1].id,  # Squats
            reps=8,
            sets=4,
            duration_seconds=None
        ),
        WorkoutExercise(
            workout_id=workouts[2].id,
            exercise_id=exercises[6].id,  # Plank
            reps=None,
            sets=3,
            duration_seconds=120  # 2 minutes
        ),
        WorkoutExercise(
            workout_id=workouts[2].id,
            exercise_id=exercises[7].id,  # Barbell Rows
            reps=8,
            sets=4,
            duration_seconds=None
        ),
    ]
    db.session.add_all(workout_exercises)
    db.session.commit()
    
    print(" Database seeded successfully!")
    print(f"   - {len(exercises)} exercises created")
    print(f"   - {len(workouts)} workouts created")
    print(f"   - {len(workout_exercises)} workout exercise records created")