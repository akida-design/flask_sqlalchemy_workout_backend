#!/usr/bin/env python3

from app import app
from models import db, Exercise, Workout, WorkoutExercise
from datetime import date

with app.app_context():
    # Reset data
    db.drop_all()
    db.create_all()
    
    # Create sample exercises
    push_ups = Exercise(name='Push-ups', category='Chest', equipment_needed=False)
    squats = Exercise(name='Squats', category='Legs', equipment_needed=False)
    bench_press = Exercise(name='Bench Press', category='Chest', equipment_needed=True)
    deadlifts = Exercise(name='Deadlifts', category='Back', equipment_needed=True)
    
    db.session.add_all([push_ups, squats, bench_press, deadlifts])
    db.session.commit()
    
    # Create sample workouts
    workout1 = Workout(date=date(2026, 5, 26), duration_minutes=45, notes='Upper body strength')
    workout2 = Workout(date=date(2026, 5, 25), duration_minutes=60, notes='Lower body and cardio')
    
    db.session.add_all([workout1, workout2])
    db.session.commit()
    
    # Create workout exercises (join table entries)
    we1 = WorkoutExercise(workout_id=workout1.id, exercise_id=push_ups.id, reps=10, sets=3)
    we2 = WorkoutExercise(workout_id=workout1.id, exercise_id=bench_press.id, reps=8, sets=4)
    we3 = WorkoutExercise(workout_id=workout2.id, exercise_id=squats.id, reps=12, sets=3)
    we4 = WorkoutExercise(workout_id=workout2.id, exercise_id=deadlifts.id, reps=5, sets=5)
    
    db.session.add_all([we1, we2, we3, we4])
    db.session.commit()
    
    print("✓ Database seeded successfully!")