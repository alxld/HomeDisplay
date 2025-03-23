from globals import workout_host, workout_user, workout_password
import mysql.connector
import sys
import time

class WorkoutDB:
    def __init__(self):
        self._db = mysql.connector.connect(
            host=workout_host,
            user=workout_user,
            password=workout_password,
            database="workout_tracker"
        )
        self._cursor = self._db.cursor()

    def db_insert_new_user(self, username, firstname, lastname):
        self._cursor.execute("INSERT INTO users (username, firstname, lastname) VALUES (%s, %s, %s)", (username, firstname, lastname))
        self._db.commit()
        return self._cursor.lastrowid

    def db_insert_new_exercise(self, name, description, comments):
        self._cursor.execute("INSERT INTO exercises (name, description, comments) VALUES (%s, %s, %s)", (name, description, comments))
        self._db.commit()
        return self._cursor.lastrowid

    def db_insert_new_set(self, exercise_id, user_id, weight, reps):
        self._cursor.execute("INSERT INTO sets (exercise_id, user_id, weight, reps) VALUES (%s, %s, %s, %s)", (exercise_id, user_id, weight, reps))
        self._db.commit()
        return self._cursor.lastrowid

    def db_get_body_parts(self):
        self._cursor.execute("SELECT * FROM body_parts")
        return self._cursor.fetchall()
    
    def db_insert_body_part(self, name):
        self._cursor.execute("INSERT INTO body_parts (body_part_name) VALUES (%s)", (name,))
        self._db.commit()
        return self._cursor.lastrowid

    # Using the exercise_body_parts table, get all the exercises that target a specific body part
    def db_get_exercises_by_body_part(self, body_part_id):
        self._cursor.execute("SELECT * FROM exercises WHERE id IN (SELECT exercise_id FROM exercise_body_parts WHERE body_part_id = %s)", (body_part_id,))
        return self._cursor.fetchall()    

    def db_get_exercises(self):
        self._cursor.execute("SELECT * FROM exercises")
        return self._cursor.fetchall()

    def db_get_sets(self, exercise_id):
        self._cursor.execute("SELECT * FROM sets WHERE exercise_id = %s", (exercise_id,))
        return self._cursor.fetchall()

    def db_get_users(self):
        self._cursor.execute("SELECT * FROM users")
        return self._cursor.fetchall()

    def db_get_user_id(self, name):
        self._cursor.execute("SELECT id FROM users WHERE name = %s", (name,))
        return self._cursor.fetchone()[0]

    def db_get_exercise_id(self, name):
        self._cursor.execute("SELECT id FROM exercises WHERE name = %s", (name,))
        return self._cursor.fetchone()[0]

    def db_get_last_set(self, exercise_id, user_id):
        self._cursor.execute("SELECT * FROM sets WHERE exercise_id = %s AND user_id = %s ORDER BY id DESC LIMIT 1", (exercise_id, user_id))
        return self._cursor.fetchone()

    def db_get_user_name(self, user_id):
        self._cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
        return self._cursor.fetchone()[0]

    def db_get_exercise_name(self, exercise_id):
        self._cursor.execute("SELECT name FROM exercises WHERE id = %s", (exercise_id,))
        return self._cursor.fetchone()[0]

    def db_get_user_sets(self, user_id):
        self._cursor.execute("SELECT * FROM sets WHERE user_id = %s", (user_id,))
        return self._cursor.fetchall()
