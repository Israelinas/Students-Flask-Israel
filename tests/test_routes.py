import requests


def test_homepage():
    r = requests.get("http://127.0.0.1:5000")
    assert r.status_code == 200

def test_students():
    r = requests.get("http://127.0.0.1:5000/students")
    assert r.status_code == 200

def test_teachers():
    r = requests.get("http://127.0.0.1:5000/teachers")
    assert r.status_code == 200

def test_courses():
    r = requests.get("http://127.0.0.1:5000/courses")
    assert r.status_code == 200

def test_teacher_profile():    
    r = requests.get("http://127.0.0.1:5000/update_profile/teacher")
    assert r.status_code == 403


def test_teacher_student():    
    r = requests.get("http://127.0.0.1:5000/update_profile/student")
    assert r.status_code == 403

def test_admin():    
        r = requests.get("http://127.0.0.1:5000/admin")
        assert r.status_code == 403

