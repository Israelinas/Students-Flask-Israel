from flask import Flask, render_template, redirect, url_for, request, session, abort, jsonify
from setup_db import execute_query
import crud
import base64
import sqlite3
import datetime
import random


app = Flask(__name__)


### SHOW STUDENTS OLD
@app.route('/students_old')
def show_students_old():
    students_tupple = execute_query(f"""
        SELECT name
             , gender
             , phone
             , birth_date
             , round((julianday(CURRENT_DATE)-julianday(birth_date))/365,2) as age
             , email
        FROM students
        INNER JOIN users ON students.user_id = users.user_id
        """)
    students = [ [student for student in student_tup] for student_tup in students_tupple ]
    images_blob = execute_query("SELECT image FROM students")
    blob_list = [image_blob[0] for image_blob in images_blob]
    images = []
    for image in blob_list:
        try:
            encoded_data = [base64.b64encode(image).decode('utf-8')]
            images.append(encoded_data)
        except:
            images.append(list("null"))
    student_images = list(map(list.__add__, students, images))
    return render_template('students_old.html', students=student_images)


### SHOW TEACHERS OLD
@app.route('/teachers_old')
def show_teachers_old():
    teachers_tupple = execute_query(f"""
    SELECT teachers.name
         , gender
         , phone
         , birth_date
         , round((julianday(CURRENT_DATE)-julianday(birth_date))/365,2) as AGE
         , email
    FROM teachers
    JOIN users ON teachers.user_id = users.user_id
    """)
    teachers = [ [teacher for teacher in teacher_tup] for teacher_tup in teachers_tupple ]
    image_blobs = execute_query("SELECT image FROM teachers")
    blob_list = [image_blob[0] for image_blob in image_blobs]
    images = []
    for image in blob_list:
        try:
            encoded_data = [base64.b64encode(image).decode('utf-8')]
            images.append(encoded_data)
        except:
            images.append(list("null"))
    teacher_images = list(map(list.__add__, teachers, images))
    return render_template('teachers_old.html', teachers=teacher_images)


## SHOW COURSES OLD
@app.route('/courses_old')
def show_courses_old():
    courses = execute_query("SELECT * FROM courses")
    return render_template('courses_old.html', courses=courses)