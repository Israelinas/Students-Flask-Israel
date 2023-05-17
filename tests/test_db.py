import sys
import os


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # get one folder back
sys.path.insert(0, parent_dir)

from setup_db import execute_query


def test_students():
    students_num = int(execute_query("SELECT COUNT(student_id) FROM students")[0][0])
    assert students_num == 40


def test_teachers():
    teachers_num = int(execute_query("SELECT COUNT(teacher_id) FROM teachers")[0][0])
    assert teachers_num == 10


def test_courses():
    courses_num = int(execute_query("SELECT COUNT(course_id) FROM courses")[0][0])
    assert courses_num == 6


def test_users():
    students_num = int(execute_query("SELECT COUNT(student_id) FROM students")[0][0])
    teachers_num = int(execute_query("SELECT COUNT(teacher_id) FROM teachers")[0][0])
    user_num = int(execute_query("SELECT COUNT(user_id) FROM users")[0][0])
    assert user_num == students_num + teachers_num + 1