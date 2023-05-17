from setup_db import execute_query, executemany_query


def convert_pic():
    files = ["./static/img/anonymous_male.jpg", "./static/img/anonymous_female.jpg"]
    picture = [open(file, "rb").read() for file in files]
    return picture

# show all from table
def show_all(table):
    return execute_query(f"""
    SELECT * 
    FROM {table}
    """)

# get course by id
def show_all_by_id(table, id):
    execute_query(f"""
    SELECT * 
    FROM {table} 
    WHERE {table}_id = {id}
    """)

# admin:
# add new user by role and can add all information - student or teacher
def new_user(email, password, role):
    execute_query(f"""
    INSERT INTO users ('email', 'password', 'role') 
    VALUES ('{email}', '{password}', '{role}')
    """)

# add profile
def new_profile(table, user_id:int, name, gender, birth_date, phone, address):
    image_list = convert_pic()
    if gender == "Female":
        image = image_list[1]
    else:
        image = image_list[0]

    execute_query(f"""
    INSERT INTO {table} ('user_id', 'name', 'image', 'gender', 'birth_date', 'phone', 'address') 
    VALUES ('{user_id}', '{name}', '{image}', '{gender}', '{birth_date}', '{phone}', '{address}')
    """)

# update user
def update_user(table, name, image, gender, birth_date, phone, address, id:int):
    execute_query(f"""
    UPDATE {table}
    SET name={name}, image={image}, gender={gender}, 
    birth_date={birth_date}, phone={phone}, address={address}
    WHERE {table}_id = {id}
    """)

# delete user
def delete(table, id:int):
    execute_query(f"""
    DELETE FROM {table} 
    WHERE {table}_id = {int(id)}
    """)


# add new course
def add_course(name, desc):
    execute_query(f"""
    INSERT INTO courses ('name', 'desc')
    VALUES('{name}','{desc}')
    """)

# update course
def update_course(id, name, desc):
    execute_query(f"""
    UPDATE courses 
    SET name={name}, desc={desc} WHERE course_id = {id}
    """)

# add active course : add teacher by teacher_id / course_id
def add_active_course(course_id, teacher_id, start_date, end_date):
    execute_query(f"""
    INSERT INTO active_courses ('course_id', 'teacher_id', 'start_date', 'end_date')
    VALUES ('{course_id}', '{teacher_id}', '{start_date}', '{end_date}')
    """)

# update active course
def update_active_course(teacher_id, start_date, end_date, id):
    execute_query(f"""
    UPDATE courses
    SET teacher_id = {teacher_id}, start_date={start_date}, end_date={end_date}
    WHERE active_course_id={id}
    """)

# add students to active course : by student_id / active_course_id
def add_active_course_student(active_course_id, student_id):
    execute_query(f"""
    INSERT INTO students_courses ('active_course_id', 'student_id')
    VALUES ('{active_course_id}', '{student_id}')
    """)

# update students to active course
def update_active_course_student(grade):
    execute_query(f"""
    UPDATE students_courses 
    SET grade={grade}
    """)
