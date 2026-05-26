from marshmallow import Schema, fields, validate, ValidationError, post_load, pre_load
from models import Exercise, Workout, WorkoutExercise
from datetime import date

# EXERCISE SCHEMA

class ExerciseSchema(Schema):
    """Schema for Exercise model"""
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, error='Exercise name must be at least 2 characters long'),
            validate.Regexp(
                r'^[a-zA-Z\s\-]+$',
                error='Exercise name can only contain letters, spaces, and hyphens'
            )
        ],
        error_messages={'required': 'Exercise name is required'}
    )
    category = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, error='Category must be at least 2 characters long'),
            validate.OneOf(
                ['Chest', 'Back', 'Legs', 'Core', 'Shoulders', 'Arms', 'Cardio'],
                error='Category must be one of: Chest, Back, Legs, Core, Shoulders, Arms, Cardio'
            )
        ],
        error_messages={'required': 'Category is required'}
    )
    equipment_needed = fields.Bool(load_default=False)
    
    class Meta:
        model = Exercise
    
    @pre_load
    def strip_whitespace(self, data, **kwargs):
        """Strip whitespace from string fields"""
        if isinstance(data, dict):
            if 'name' in data and isinstance(data['name'], str):
                data['name'] = data['name'].strip()
            if 'category' in data and isinstance(data['category'], str):
                data['category'] = data['category'].strip()
        return data
    
    @post_load
    def make_exercise(self, data, **kwargs):
        """Convert deserialized data to Exercise instance"""
        return Exercise(**data)


# WORKOUT EXERCISE SCHEMA

class WorkoutExerciseSchema(Schema):
    """Schema for WorkoutExercise model"""
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(
        required=True,
        error_messages={'required': 'Workout ID is required'}
    )
    exercise_id = fields.Int(
        required=True,
        error_messages={'required': 'Exercise ID is required'}
    )
    reps = fields.Int(
        allow_none=True,
        validate=validate.Range(
            min=1,
            error='Reps must be a positive integer (at least 1)'
        )
    )
    sets = fields.Int(
        allow_none=True,
        validate=validate.Range(
            min=1,
            error='Sets must be a positive integer (at least 1)'
        )
    )
    duration_seconds = fields.Int(
        allow_none=True,
        validate=validate.Range(
            min=1,
            error='Duration must be a positive integer (at least 1 second)'
        )
    )
    
    class Meta:
        model = WorkoutExercise
    
    @post_load
    def validate_metrics(self, data, **kwargs):
        """
        VALIDATION 1: Ensure at least one of reps, sets, or duration_seconds is provided
        Mirrors the CheckConstraint in the WorkoutExercise model
        """
        if not any([data.get('reps'), data.get('sets'), data.get('duration_seconds')]):
            raise ValidationError(
                'At least one of reps, sets, or duration_seconds must be provided'
            )
        
        # VALIDATION 2: Validate realistic ranges for metrics
        reps = data.get('reps')
        sets = data.get('sets')
        duration_seconds = data.get('duration_seconds')
        
        if reps and reps > 1000:
            raise ValidationError('Reps cannot exceed 1000 in a single set')
        
        if sets and sets > 100:
            raise ValidationError('Sets cannot exceed 100 for a single exercise')
        
        if duration_seconds and duration_seconds > 3600:  # 1 hour
            raise ValidationError('Duration cannot exceed 3600 seconds (1 hour) per exercise')
        
        return WorkoutExercise(**data)


# NESTED SCHEMAS (for relationships)

class ExerciseNestedSchema(Schema):
    """Nested schema for Exercise (used in Workout responses)"""
    id = fields.Int()
    name = fields.Str()
    category = fields.Str()
    equipment_needed = fields.Bool()


class WorkoutExerciseNestedSchema(Schema):
    """Nested schema for WorkoutExercise (includes exercise details)"""
    id = fields.Int()
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
    exercise = fields.Nested(ExerciseNestedSchema)


# WORKOUT SCHEMA

class WorkoutSchema(Schema):
    """Schema for Workout model"""
    id = fields.Int(dump_only=True)
    date = fields.Date(
        required=True,
        error_messages={'required': 'Date is required'}
    )
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(
            min=1,
            error='Duration must be a positive integer (at least 1 minute)'
        ),
        error_messages={'required': 'Duration in minutes is required'}
    )
    notes = fields.Str(
        allow_none=True,
        validate=validate.Length(
            max=1000,
            error='Notes cannot exceed 1000 characters'
        )
    )
    
    class Meta:
        model = Workout
    
    @post_load
    def validate_workout(self, data, **kwargs):
        """
        VALIDATION 3: Ensure workout date is not in the future
        Mirrors the validate_date validator in the Workout model
        """
        workout_date = data.get('date')
        if workout_date and workout_date > date.today():
            raise ValidationError('Workout date cannot be in the future')
        
        # VALIDATION 4: Ensure duration doesn't exceed realistic limits
        duration = data.get('duration_minutes')
        if duration and duration > 480:  # 8 hours
            raise ValidationError('Workout duration cannot exceed 480 minutes (8 hours)')
        
        return Workout(**data)


class WorkoutDetailSchema(Schema):
    """Extended schema for Workout with nested exercises (for GET detail)"""
    id = fields.Int(dump_only=True)
    date = fields.Date()
    duration_minutes = fields.Int()
    notes = fields.Str(allow_none=True)
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseNestedSchema))


# INSTANTIATE SCHEMAS

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_schema = WorkoutExerciseSchema()
workout_exercises_schema = WorkoutExerciseSchema(many=True)