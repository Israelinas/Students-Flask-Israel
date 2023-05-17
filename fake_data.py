from setup_db import execute_query, executemany_query
from faker import Faker
from random import choice, randint

fake = Faker()

def add_fake_user(role, num):
    users = [(role, fake.email(), fake.password()) for i in range(num)]
    executemany_query("""
        INSERT INTO users (role, email, password)
        VALUES (?, ?, ?)
        """, users)


def add_fake_profile(table, role, num, faker_seed, slice, max, min):
    add_fake_user(role, num)
    Faker.seed(faker_seed)
    user_db = execute_query(f"SELECT user_id FROM users WHERE role='{role}'")
    user_ids = [int(user_id[0]) for user_id in user_db]
    male_profiles = [
        (user_id, f"{fake.first_name_male()} {fake.last_name()}", "../static/img/anonymous_male.jpg", "Male",
         fake.date_of_birth(minimum_age=min, maximum_age=max), fake.phone_number(), fake.address(), )
        for user_id in user_ids[:slice]
    ]
    female_profiles = [
        (user_id, f"{fake.first_name_female()} {fake.last_name()}", "../static/img/anonymous_female.jpg", "Female",
         fake.date_of_birth(minimum_age=min, maximum_age=max), fake.phone_number(), fake.address(), )
        for user_id in user_ids[slice:]
    ]
    executemany_query(f"""
        INSERT INTO {table} (
            user_id, name, image, gender, birth_date, phone, address
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, male_profiles + female_profiles)


def add_course():
    course_names = ["Python", "Java", "C++", "C#", "JavaScript", "PHP"]
    course_desc = [
        "Python is a computer programming language often used to build websites and software, automate tasks, and conduct data analysis. Python is a general-purpose language, meaning it can be used to create a variety of different programs and isn't specialized for any specific problems.",
        "Java is a widely used object-oriented programming language and software platform that runs on billions of devices, including notebook computers, mobile devices, gaming consoles, medical devices and many others. The rules and syntax of Java are based on the C and C++ languages.",
        "C++ is an object-oriented programming language which gives a clear structure to programs and allows code to be reused, lowering development costs. C++ is portable and can be used to develop applications that can be adapted to multiple platforms.",
        "C# is an object-oriented, component-oriented programming language. C# provides language constructs to directly support these concepts, making C# a natural language in which to create and use software components. Since its origin, C# has added features to support new workloads and emerging software design practices.",
        "JavaScript (JS) is a lightweight, interpreted, or just-in-time compiled programming language with first-class functions. While it is most well-known as the scripting language for Web pages, many non-browser environments also use it, such as Node.js, Apache CouchDB and Adobe Acrobat. JavaScript is a prototype-based, multi-paradigm, single-threaded, dynamic language, supporting object-oriented, imperative, and declarative (e.g. functional programming) styles.",
        "PHP is an open-source server-side scripting language that many devs use for web development. It is also a general-purpose language that you can use to make lots of projects, including Graphical User Interfaces (GUIs)."
    ]
    course_images = ['../static/img/python_pic.jpg', '../static/img/java_pic.jpg', '../static/img/cplusplus_pic.jpg', '../static/img/csharp_pic.jpg', '../static/img/javascript_pic.jpg', '../static/img/php_pic.jpg']
    course_syllabus = ['../static/img/Python_Syllabus.pdf', '../static/img/Java_Syllabus.pdf', '../static/img/C++_Syllabus.pdf', '../static/img/C#_Syllabus.pdf', '../static/img/JavaScript_Syllabus.pdf', '../static/img/PHP_Syllabus.pdf']
    courses = dict(zip(course_names, zip(course_desc, course_images, course_syllabus)))
       
    course_list = [(course, courses[course][0], courses[course][1], courses[course][2]) for course in courses]
    executemany_query("""
        INSERT INTO courses (name, desc, image, syllabus)
        VALUES (?, ?, ?, ?)
        """, course_list)


def create_active_course():
    teacher_db = execute_query("SELECT teacher_id FROM teachers")
    teacher_ids = [int(teacher[0]) for teacher in teacher_db]
    course_db = execute_query("SELECT course_id FROM courses")
    course_ids = [int(course[0]) for course in course_db]
    teacher_course_ids = [
        (teacher, choice(course_ids), f"2023-02-{randint(10,28)}", f"2023-08-{randint(10,28)}")
        for teacher in teacher_ids
    ]
    executemany_query("""
        INSERT INTO active_courses (
            teacher_id, course_id, start_date, end_date
        )
        VALUES (?, ?, ?, ?)
    """, teacher_course_ids)


def add_student_to_active_course():
    student_db = execute_query("SELECT student_id FROM students")
    student_ids = [student[0] for student in student_db]
    active_course_db = execute_query("SELECT active_course_id FROM active_courses")
    active_course_ids = [course[0] for course in active_course_db]
    student_course_ids = [
        (teacher, choice(active_course_ids), randint(70, 100))
        for teacher in student_ids
    ]
    executemany_query("""
        INSERT INTO students_courses (
            student_id, active_course_id, grade
        )
        VALUES (?, ?, ?)
    """, student_course_ids)


if __name__ == "__main__":
    add_fake_profile(
        table="students", role='Student', num=40, faker_seed=0, slice=15, min=21, max=40
    )
    add_fake_profile(
        table="teachers", role='Teacher', num=10, faker_seed=1, slice=3, min=35, max=70
    )
    add_course()
    create_active_course()
    add_student_to_active_course()
