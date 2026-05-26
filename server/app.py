from flask import Flask, make_response, request, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from datetime import date

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema, exercises_schema,
    workout_schema, workouts_schema, workout_detail_schema,
    workout_exercise_schema, workout_exercises_schema
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# WORKOUT ENDPOINTS

@app.route('/workouts', methods=['GET'])
def get_workouts():
    """List all workouts"""
    try:
        workouts = Workout.query.all()
        return make_response(workouts_schema.dump(workouts), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    """Show a single workout with its associated exercises"""
    try:
        workout = Workout.query.get(id)
        
        if not workout:
            return make_response(jsonify({'error': 'Workout not found'}), 404)
        
        # Use workout_detail_schema to include nested workout_exercises with exercise details
        return make_response(workout_detail_schema.dump(workout), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/workouts', methods=['POST'])
def create_workout():
    """Create a workout"""
    try:
        data = request.get_json()
        
        if not data:
            return make_response(jsonify({'error': 'Request body is required'}), 400)
        
        # Deserialize and validate data using schema
        workout = workout_schema.load(data)
        
        # Add to session and commit
        db.session.add(workout)
        db.session.commit()
        
        return make_response(workout_schema.dump(workout), 201)
    
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    """Delete a workout (cascades to associated WorkoutExercises)"""
    try:
        workout = Workout.query.get(id)
        
        if not workout:
            return make_response(jsonify({'error': 'Workout not found'}), 404)
        
        # Delete associated WorkoutExercises (cascade is handled by relationship)
        db.session.delete(workout)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Workout deleted successfully'}), 200)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 500)


# EXERCISE ENDPOINTS

@app.route('/exercises', methods=['GET'])
def get_exercises():
    """List all exercises"""
    try:
        exercises = Exercise.query.all()
        return make_response(exercises_schema.dump(exercises), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    """Show an exercise and associated workouts"""
    try:
        exercise = Exercise.query.get(id)
        
        if not exercise:
            return make_response(jsonify({'error': 'Exercise not found'}), 404)
        
        # Serialize exercise with its associated workouts
        exercise_data = exercise_schema.dump(exercise)
        
        # Add associated workouts to response
        workouts = [
            {
                'id': w.id,
                'date': w.date.isoformat(),
                'duration_minutes': w.duration_minutes,
                'notes': w.notes
            }
            for w in exercise.workouts
        ]
        exercise_data['workouts'] = workouts
        
        return make_response(jsonify(exercise_data), 200)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    """Create an exercise"""
    try:
        data = request.get_json()
        
        if not data:
            return make_response(jsonify({'error': 'Request body is required'}), 400)
        
        # Check if exercise with same name already exists (unique constraint)
        existing_exercise = Exercise.query.filter_by(name=data.get('name')).first()
        if existing_exercise:
            return make_response(
                jsonify({'error': 'An exercise with this name already exists'}), 400
            )
        
        # Deserialize and validate data using schema
        exercise = exercise_schema.load(data)
        
        # Add to session and commit
        db.session.add(exercise)
        db.session.commit()
        
        return make_response(exercise_schema.dump(exercise), 201)
    
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 500)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    """Delete an exercise (cascades to associated WorkoutExercises)"""
    try:
        exercise = Exercise.query.get(id)
        
        if not exercise:
            return make_response(jsonify({'error': 'Exercise not found'}), 404)
        
        # Delete associated WorkoutExercises (cascade is handled by relationship)
        db.session.delete(exercise)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Exercise deleted successfully'}), 200)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 500)


# WORKOUT EXERCISE ENDPOINTS

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    """Add an exercise to a workout, including reps/sets/duration"""
    try:
        # Verify workout exists
        workout = Workout.query.get(workout_id)
        if not workout:
            return make_response(jsonify({'error': 'Workout not found'}), 404)
        
        # Verify exercise exists
        exercise = Exercise.query.get(exercise_id)
        if not exercise:
            return make_response(jsonify({'error': 'Exercise not found'}), 404)
        
        # Check if the combination already exists (unique constraint)
        existing = WorkoutExercise.query.filter_by(
            workout_id=workout_id,
            exercise_id=exercise_id
        ).first()
        if existing:
            return make_response(
                jsonify({'error': 'This exercise is already added to this workout'}), 400
            )
        
        data = request.get_json()
        
        if not data:
            return make_response(jsonify({'error': 'Request body is required'}), 400)
        
        # Add workout_id and exercise_id to data
        data['workout_id'] = workout_id
        data['exercise_id'] = exercise_id
        
        # Deserialize and validate data using schema
        workout_exercise = workout_exercise_schema.load(data)
        
        # Add to session and commit
        db.session.add(workout_exercise)
        db.session.commit()
        
        return make_response(workout_exercise_schema.dump(workout_exercise), 201)
    
    except ValidationError as err:
        return make_response(jsonify({'errors': err.messages}), 400)
    except Exception as e:
        db.session.rollback()
        return make_response(jsonify({'error': str(e)}), 500)


# ERROR HANDLERS

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return make_response(jsonify({'error': 'Resource not found'}), 404)


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return make_response(jsonify({'error': 'Internal server error'}), 500)


if __name__ == '__main__':
    app.run(port=5555, debug=True)