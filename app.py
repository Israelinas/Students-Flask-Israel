from flask import Flask, render_template, redirect, url_for, request, session, abort, jsonify, flash
from setup_db import execute_query
import crud
import datetime
import random
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

app.secret_key = 'crocodile-dundee'

app.config['UPLOAD_FOLDER'] = './static/img'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


## TIME MESSAGE ##
def time_message():
    now = datetime.datetime.now()
    if now.hour >= 5 and now.hour < 12:
        message = "Good morning"
        return message
    elif now.hour >= 12 and now.hour < 18:
        message = "Good afternoon"
        return message
    else:
        message = "Good evening"
        return message


## BEFORE REQUEST - SESSION ##
@app.before_request
def auth():
    path_teacher_list = ['/teacher_panel']
    # path_student_list = ['/student']
    if "role" not in session.keys():
        session["username"]='anonymous'
        session["role"]='anonymous'
    if session["role"] != 'Admin':
        if 'admin' in request.full_path:
            return abort(403)
    if session["role"] != 'Teacher':
        if any(route in request.full_path for route in path_teacher_list):
            return abort(403)
    # if session["role"] != ['Student']:
    #     if any(route in request.full_path for route in path_student_list):
    #         return abort(403)

               
## HOME PAGE ##
@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'GET':
        students_num = execute_query("SELECT COUNT(student_id) FROM students")
        teachers_num = execute_query("SELECT COUNT(teacher_id) FROM teachers")
        courses_num = execute_query("SELECT COUNT(course_id) FROM courses")
        active_courses_num = execute_query("SELECT COUNT(active_course_id) FROM active_courses")

        new_courses = execute_query(f"""
        SELECT name, start_date, end_date from active_courses
        JOIN courses ON active_courses.course_id = courses.course_id
        ORDER BY start_date
        DESC LIMIT 5
        """)
        teacher_names = []
        teacher_images = []
        teachers_tuple = execute_query("SELECT * FROM teachers")
        for teacher in teachers_tuple:
            teacher_names.append(teacher[2])
            teacher_images.append(teacher[3])
        random_names = random.sample(teacher_names, 3)
        random_images = [teacher_images[teacher_names.index(name)] for name in random_names]

        for teacher_name, teacher_image in zip(random_names, random_images):
            teacher_name, teacher_image

        student_names = []
        student_images = []
        students_tuple = execute_query("SELECT * FROM students")
        for student in students_tuple:
            student_names.append(student[2])
            student_images.append(student[3])
        random_names = random.sample(student_names, 3)
        random_images = [student_images[student_names.index(name)] for name in random_names]

        for student_name, student_image in zip(random_names, random_images):
            student_name, student_image
        
        return render_template("index.html", new_courses=new_courses, teacher_name=teacher_name, teacher_image=teacher_image, student_name=student_name, student_image=student_image, students_num=students_num, teachers_num=teachers_num, courses_num=courses_num, active_courses_num=active_courses_num)
    else:
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        city = request.form["city"]
        execute_query(f"""
        INSERT INTO leads (name, phone, email, city)
        VALUES ('{name}','{phone}','{email}','{city}')
        """)
        try:
            return render_template("index.html", name=name, phone=phone, email=email, city=city)
        except:
            return redirect(url_for("home"))
        

@app.route('/api/messages')
def get_messages():
    query = execute_query('SELECT message FROM messages ORDER BY message_id DESC LIMIT 3')
    messages = ['▶ ' +row[0] for row in query]
    return jsonify(messages)


## ADMIN PAGE VIEW ##
@app.route('/admin')
def admin():
    teachers = crud.show_all(table="teachers")
    courses = crud.show_all(table="courses")
    active_courses = execute_query(f"""
    SELECT active_courses.active_course_id, 
           courses.name
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    """)
    students = crud.show_all(table="students")
    roles = execute_query(f"SELECT DISTINCT role FROM users")
    message = time_message()
    return render_template("admin.html", teachers=teachers, courses=courses, active_courses=active_courses, students=students, roles = roles, message=message)


## ADMIN - CREATE A NEW COURSE ##
@app.route('/admin/create_course', methods=["POST"])
def create_course():
    course_name = request.form['course_name']
    course_desc = request.form['course_desc']
    
    course_image_path = None
    course_syllabus_path = None

    course_image = request.files['course_image']
    if course_image and allowed_file(course_image.filename):
        filename = secure_filename(course_image.filename)
        course_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        course_image_path = ".." + url_for('static', filename='img/' + filename)

    course_syllabus = request.files['course_syllabus']
    if course_syllabus and allowed_file(course_syllabus.filename):
        filename = secure_filename(course_syllabus.filename)
        course_syllabus.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        course_syllabus_path = ".." + url_for('static', filename='img/' + filename)

    execute_query(f"""
    INSERT INTO courses ('name', 'desc', 'image', 'syllabus')
    VALUES ('{course_name}', '{course_desc}', '{course_image_path}', '{course_syllabus_path}')
    """)
    return redirect(url_for("admin"))


## ADMIN - CREATE ACTIVE COURSE (SET TEACHER AND DATES) ##
@app.route('/admin/active_course', methods=["POST"])
def teacher_course():
    course_id = request.form['course_id']
    teacher_id = request.form['teacher_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    crud.add_active_course(course_id=course_id, teacher_id=teacher_id, start_date=start_date, end_date=end_date)
    return redirect(url_for("admin"))


## ADMIN - UPLOAD IMAGE TO AN EXISTING COURSE ##
@app.route('/admin/upload_image_to_course', methods=["POST"])
def upload_image_to_course():
    course_id=request.form["course_id"]
    image = request.files["image"]

    image_path = None
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        image_path = ".." + url_for('static', filename='img/' + filename)
    execute_query(f"""
        UPDATE courses
        SET image = '{image_path}'
        WHERE course_id = {course_id}
    """)
    return redirect(url_for('admin'))

## ADMIN UPLOAD SYLLABUS TO COURSE ##
@app.route('/admin/upload_syllabus_to_course', methods=["POST"])
def upload_syllabus_to_course():
    course_id=request.form["course_id"]
    syllabus = request.files["syllabus"]

    syllabus_path = None
    if syllabus and allowed_file(syllabus.filename):
        filename = secure_filename(syllabus.filename)
        syllabus.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        syllabus_path = ".." + url_for('static', filename='img/' + filename)
    execute_query(f"""
        UPDATE courses
        SET syllabus = '{syllabus_path}'
        WHERE course_id = {course_id}
    """)
    return redirect(url_for('admin'))

## ADMIN - SHOW ACTIVE COURSES
@app.route('/admin/active_courses')
def admin_active_courses():
    teachers = execute_query("SELECT * FROM teachers")
    active_courses = execute_query(f"""
    SELECT active_course_id
         , courses.name
         , teachers.name
         , start_date
         , end_date
         , courses.image
         , teachers.teacher_id
    FROM active_courses
    LEFT JOIN courses ON active_courses.course_id = courses.course_id
    LEFT JOIN teachers ON active_courses.teacher_id = teachers.teacher_id
    """)
    return render_template('admin_active_courses.html', active_courses=active_courses, teachers=teachers)


@app.route('/admin/active_courses/delete', methods=['POST'])
def admin_active_courses_delete():
    active_course_id = request.form['active_course_id']
    execute_query(f"DELETE FROM active_courses WHERE active_course_id = {active_course_id}")
    return redirect(url_for('admin_active_courses'))
    

@app.route('/admin/active_courses/update', methods=['POST'])
def admin_active_courses_update():
    active_course_id = request.form['active_course_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    teacher_id = request.form['teacher_id']
    execute_query(f"""
            UPDATE active_courses
            SET start_date = '{start_date}', end_date = '{end_date}', teacher_id = {teacher_id}
            WHERE active_course_id = {active_course_id}
            """)
    return redirect(url_for("admin_active_courses"))

          

## ADD MESSAGE ##
@app.route('/admin/admin_messages', methods=['POST'])
def admin_messages():
    message = request.form["message"]
    execute_query(f"""
    INSERT INTO messages ('message')
    VALUES ('{message}')
    """)
    return redirect(url_for("admin"))

    
## LEADS ##
@app.route('/admin/leads', methods = ['GET', 'POST'])
def show_leads():
    if request.method == 'GET':
        leads = execute_query("SELECT * FROM leads")
        return render_template("leads.html", leads=leads)
    else:
        lead_id = request.form['lead_id']
        if request.form.get('update_status'):
            status = request.form['status']
            execute_query(f"""
            UPDATE leads
            SET status = '{status}'
            WHERE lead_id = {lead_id}
            """)
        elif request.form.get('delete_lead'):
            execute_query(f"DELETE FROM leads WHERE lead_id = {lead_id}")
        return redirect(url_for("show_leads"))


### ADD STUDENT TO COURSE
@app.route('/admin/course_student', methods=["POST"])
def method_name():
    active_course_id = request.form['active_course_id']
    student_id = request.form['student_id']
    crud.add_active_course_student(active_course_id=active_course_id, student_id=student_id)
    return redirect(url_for("admin"))


### NEW USER REGISTRATION
@app.route('/register', methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    role = request.form["role"]
    crud.new_user(email=email, password=password, role=role)
    return redirect(url_for("admin"))


## ADMIN - SHOW STUDENTS ##
@app.route('/admin/show_students', methods = ['GET', 'POST'])
def admin_show_students():
    if request.method == 'GET':
        query = request.args.get('q')
        if query:
            students_tupple = execute_query(f"""
                SELECT name
                    , gender
                    , phone
                    , birth_date
                    , round((julianday(CURRENT_DATE)-julianday(birth_date))/365,2) as age
                    , email
                FROM students
                INNER JOIN users ON students.user_id = users.user_id
                WHERE name LIKE '%{query}%'
                """)
        else:
            students_tupple = execute_query(f"""
                SELECT students.name
                     , gender
                     , phone
                     , birth_date
                     , ROUND((julianday(CURRENT_DATE)-julianday(birth_date))/365,2) as age
                     , email
                     , GROUP_CONCAT(courses.name || ' - ' || active_courses.active_course_id, ', ') as courses
                     , ROUND(AVG(students_courses.grade), 2) as avg_grade
                     , students.student_id
                     , phone
                     , address
                     , students.image
                FROM students
                INNER JOIN users ON students.user_id = users.user_id
                LEFT JOIN students_courses ON students.student_id = students_courses.student_id
                LEFT JOIN active_courses ON students_courses.active_course_id = active_courses.active_course_id
                LEFT JOIN courses ON active_courses.course_id = courses.course_id
                GROUP BY students.student_id
                """)
        students = [ [student for student in student_tup] for student_tup in students_tupple ]
        return render_template('admin_show_students.html', students=students, query=query)
    elif request.method == 'POST':
        student_id = request.form['student_id']
        execute_query(f"DELETE FROM students WHERE student_id = {student_id}")
        return redirect(url_for("admin_show_students"))

@app.route('/admin/show_students/delete', methods=['POST'])
def admin_show_students_delete():
    student_id = request.form['student_id']
    execute_query(f"DELETE FROM students WHERE student_id = {student_id}")
    return redirect(url_for('admin_show_students'))

@app.route('/admin/show_students/update', methods=['POST'])
def admin_show_students_update():
    student_id = request.form['student_id']
    student_name = request.form['student_name']
    student_email = request.form['student_email']
    student_phone = request.form['student_phone']
    student_address = request.form['student_address']
    execute_query(f"""
    UPDATE students
    SET name = '{student_name}', 
        phone = '{student_phone}',
        address = '{student_address}'
    WHERE student_id = {student_id}
    """)
    execute_query(f"""
    UPDATE users
    SET email = '{student_email}'
    WHERE user_id = (
                    SELECT students.user_id FROM students
                    INNER JOIN users on students.user_id = users.user_id
                    WHERE students.student_id = {student_id}
                    )
    """)
    return redirect(url_for('admin_show_students'))


## ADMIN - SHOW TEACHERS ##
@app.route('/admin/show_teachers', methods=['GET', 'POST'])
def admin_show_teachers():
    if request.method == 'GET':
        teachers_tupple = execute_query(f"""
        SELECT teachers.name
            , teachers.gender
            , teachers.phone
            , teachers.birth_date
            , round((julianday(CURRENT_DATE)-julianday(teachers.birth_date))/365,2) as age
            , users.email
            , (
                SELECT GROUP_CONCAT(courses.name || ' - ' || active_courses.active_course_id, ', ')
                FROM active_courses
                JOIN courses ON active_courses.course_id = courses.course_id
                WHERE active_courses.teacher_id = teachers.teacher_id
            ) as courses
            , ROUND(AVG(grade),2) as avg_grade
            , teachers.teacher_id
            , teachers.phone
            , teachers.address
            , teachers.image
        FROM teachers
        JOIN users ON teachers.user_id = users.user_id
        LEFT JOIN active_courses ON teachers.teacher_id = active_courses.teacher_id
        LEFT JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
        GROUP BY teachers.teacher_id
        """)
        teachers = [ [teacher for teacher in teacher_tup] for teacher_tup in teachers_tupple ]
        return render_template('admin_show_teachers.html', teachers=teachers)
    elif request.method == 'POST':
        teacher_id = request.form['teacher_id']
        execute_query(f"DELETE FROM teachers WHERE teacher_id = {teacher_id}")
        return redirect(url_for("admin_show_teachers"))
    
@app.route('/admin/show_teachers/delete', methods=['POST'])
def admin_show_teachers_delete():
    teacher_id = request.form['teacher_id']
    execute_query(f"DELETE FROM teachers WHERE teacher_id = {teacher_id}")
    return redirect(url_for('admin_show_teachers'))

@app.route('/admin/show_teachers/update', methods=['POST'])
def admin_show_teachers_update():
    teacher_id = request.form['teacher_id']
    teacher_name = request.form['teacher_name']
    teacher_email = request.form['teacher_email']
    teacher_birth_date = request.form['teacher_birth_date']
    teacher_phone = request.form['teacher_phone']
    teacher_address = request.form['teacher_address']
    execute_query(f"""
    UPDATE teachers
    SET name = '{teacher_name}', 
        birth_date = '{teacher_birth_date}',
        phone = '{teacher_phone}',
        address = '{teacher_address}'
    WHERE teacher_id = {teacher_id}
    """)
    execute_query(f"""
    UPDATE users
    SET email = '{teacher_email}'
    WHERE user_id = (
                    SELECT teachers.user_id FROM teachers
                    INNER JOIN users on teachers.user_id = users.user_id
                    WHERE teachers.teacher_id = {teacher_id}
                    )
    """)
    return redirect(url_for('admin_show_teachers'))


## LOG IN ##
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user_data = execute_query(f"""
            SELECT role 
                 , user_id
            FROM users
            WHERE email='{email}' 
            AND password='{password}'
            """)
        if not user_data:
            message = "The email address or password is incorrect. Please try again"
            return render_template("login.html", message)
        session['username'] = email
        session['role'] = user_data[0][0]
        session['user_id'] = user_data[0][1]
        return redirect(url_for('home'))
    return render_template("login.html")


## LOG OUT ##
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))


## TEACHER PANEL AND UPDATE GRADE ##
@app.route('/teacher/update_grades', methods=['GET', 'POST'])
def teacher_update_grades():
    message = time_message()
    user_id = session['user_id']
    teachers = execute_query(f"""
    SELECT teacher_id,
           name
    FROM teachers
    WHERE user_id = {user_id}
    """)
    courses = execute_query(f"""
    SELECT active_courses.active_course_id,
           courses.name    
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    WHERE teacher_id = {teachers[0][0]}
    """)
    active_course_id = request.args.get("active_course_id")
    if active_course_id:
        students = execute_query(f"""
        SELECT students_courses.students_courses_id,
               students_courses.grade,
               students.student_id,
               students.name,
               courses.name
        FROM students_courses
        JOIN students ON students_courses.student_id = students.student_id
        JOIN active_courses ON students_courses.active_course_id = active_courses.active_course_id
        JOIN courses ON active_courses.course_id = courses.course_id
        WHERE active_courses.active_course_id = {active_course_id}
        """)
        selected_course = execute_query(f"""
        SELECT courses.name 
        FROM active_courses
        JOIN courses ON active_courses.course_id = courses.course_id
        WHERE active_courses.active_course_id = {active_course_id}
        """)
        return render_template("update_grades.html", students=students, courses=courses,
                               teachers=teachers, message=message, active_course_id=active_course_id, selected_course=selected_course)
    error_message = ""
    if request.method == "POST":
        try:
            active_course_id = request.form["active_course_id"]
            return redirect(url_for("teacher_update_grades", active_course_id=active_course_id), active_course_id=active_course_id)
        except:
            error_message = "Please select a course"
    return render_template("update_grades.html", courses=courses, message=message, teachers=teachers,
                           error_message=error_message)

## UPDATE GRADE ##
@app.route('/update_grade', methods=['POST'])
def update_grade():
    course_id = request.form.get('active_course_id')
    student_id = request.form.get("student_id")
    grade = request.form.get("grade")
    print(student_id, grade)
    execute_query(f"""
        UPDATE students_courses
        SET grade = '{grade}'
        WHERE student_id = '{student_id}' AND active_course_id = '{course_id}'
        """)
    return redirect(request.referrer)



### UPDATE STUDENT INFO
@app.route('/update_profile/student', methods = ['GET', 'POST'])
def update_student_profile():  
    if "user_id" not in session:
        abort(403)
    user_id = session["user_id"]
    students_db = execute_query(f"""
    SELECT name, 
           image, 
           gender, 
           birth_date, 
           phone, 
           address, 
           users.email, 
           users.password , 
           students.user_id
    FROM students
    JOIN users ON students.user_id = users.user_id
    WHERE students.user_id = {user_id}
    """)
    if request.method == 'POST' and 'personal_info' in request.form:
        name = request.form["name"].title()
        gender = request.form["gender"]
        birth_date = request.form["birth_date"]
        phone = request.form["phone"]
        address = request.form["address"]
        image = request.files["image"]

        image_path = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = ".." + url_for('static', filename='img/' + filename)

        execute_query(f"""
        UPDATE students
        SET name = '{name}'
          , image = '{image_path}'
          , gender = '{gender}'
          , birth_date = '{birth_date}'
          , phone = '{phone}'
          , address = '{address}'
        WHERE students.user_id = {user_id}
        """)
        return redirect(url_for("update_student_profile"))
    elif request.method == 'POST' and 'credentials' in request.form:
        email = request.form["email"]
        password = request.form["password"]
        execute_query(f"""
        UPDATE users
        SET email = '{email}'
          , password = '{password}'
        WHERE users.user_id = (SELECT user_id FROM students WHERE user_id = {user_id})
        """)     
        return redirect(url_for("update_student_profile"))
    message = time_message()
    return render_template("update_student_profile.html", student_info=students_db, message=message)


### UPDATE TEACHER INFO
@app.route('/update_profile/teacher', methods = ['GET', 'POST'])
def update_teacher_profile():  
    if "user_id" not in session:
        abort(403)
    user_id = session["user_id"]
    teachers_db = execute_query(f"""
    SELECT name, 
           image, 
           gender, 
           birth_date, 
           phone, 
           address, 
           users.email, 
           users.password , 
           teachers.user_id
    FROM teachers
    JOIN users ON teachers.user_id = users.user_id
    WHERE teachers.user_id = {user_id}
    """)
    if request.method == 'POST' and 'personal_info' in request.form:
        name = request.form["name"].title()
        gender = request.form["gender"]
        birth_date = request.form["birth_date"]
        phone = request.form["phone"]
        address = request.form["address"]
        image = request.files["image"]

        image_path = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = ".." + url_for('static', filename='img/' + filename)

        execute_query(f"""
        UPDATE teachers
        SET name = '{name}'
          , image = '{image_path}'
          , gender = '{gender}'
          , birth_date = '{birth_date}'
          , phone = '{phone}'
          , address = '{address}'
        WHERE teachers.user_id = {user_id}
        """)
        return redirect(url_for("update_teacher_profile"))
    elif request.method == 'POST' and 'credentials' in request.form:
        email = request.form["email"]
        password = request.form["password"]
        execute_query(f"""
        UPDATE users
        SET email = '{email}'
          , password = '{password}'
        WHERE users.user_id = (SELECT user_id FROM teachers WHERE user_id = {user_id})
        """)     
        return redirect(url_for("update_teacher_profile"))
    message = time_message()
    return render_template("update_teacher_profile.html", teacher_info=teachers_db, message=message)

     
### SHOW STUDENTS NEW
@app.route('/students')
def show_students():
    students_tupple = execute_query(f"""
        SELECT name
             , gender
             , phone
             , birth_date
             , round((julianday(CURRENT_DATE)-julianday(birth_date))/365,2) as age
             , image
             , email
        FROM students
        INNER JOIN users ON students.user_id = users.user_id
        """)
    return render_template('students.html', students=students_tupple)


### SHOW TEACHERS NEW
@app.route('/teachers')
def show_teachers():
    teachers_tupple = execute_query(f"""
    SELECT teachers.name
         , gender
         , phone
         , birth_date
         , round((julianday(CURRENT_DATE)-julianday(birth_date))/365,2) as AGE
         , teachers.image
         , email
         , GROUP_CONCAT(courses.name, ', ') as courses
    FROM teachers
    INNER JOIN users ON teachers.user_id = users.user_id
    INNER JOIN active_courses ON teachers.teacher_id = active_courses.teacher_id
    INNER JOIN courses ON active_courses.course_id = courses.course_id
    GROUP BY teachers.name, gender, phone, birth_date, email
    """)
    return render_template('teachers.html', teachers=teachers_tupple)


### SHOW COURSES NEW
@app.route('/courses')
def show_courses():
    search_text = request.args.get('search_text', '')
    query = f"SELECT * FROM courses WHERE LOWER(name) LIKE '%{search_text.lower()}%'"
    courses = execute_query(query)
    return render_template('courses.html', courses=courses)


### CHECK WHY IT DOESN'T WORK
@app.route('/newsletter_subscriber', methods =['POST'])
def newsletter_subscribe():
    subscriber_email = request.form['subscriber_email']
    execute_query(f"INSERT INTO subscribers (email) VALUES('{subscriber_email}')")
    return redirect(request.referrer)


### SEARCH IN NAVBAR
@app.route('/search')
def search():
    search = request.args["search"]
    if len(search) != 0:
        results = execute_query(f"""
        SELECT students.name, teachers.name, courses.name FROM students
        JOIN students_courses ON students.student_id = students_courses.student_id
        JOIN active_courses ON students_courses.active_course_id = active_courses.active_course_id
        JOIN teachers ON active_courses.teacher_id = teachers.teacher_id
        JOIN courses ON active_courses.course_id = courses.course_id
        WHERE students.name LIKE '{search}%'
            """)
        if len(results) != 0:
            return render_template("search.html", students = results)
        results = execute_query(f"""
        SELECT teachers.name, courses.name FROM teachers
        JOIN active_courses ON teachers.teacher_id = active_courses.teacher_id
        JOIN courses on active_courses.course_id = courses.course_id
        WHERE teachers.name LIKE '{search}%'
        """)
        if len(results) != 0:
            return render_template("search.html", teachers=results)
        results = execute_query(f"""
        SELECT name, 
               desc 
        FROM courses
        WHERE name LIKE '{search}%'
        """)
        if len(results) != 0:
            return render_template("search.html", courses=results)
        return redirect(url_for("home"))
    return redirect(request.referrer)
    

#### PROJECT 2 #####
@app.route('/attendance', methods=['GET'])
def attendance():
    message = time_message()
    user_id = session['user_id']
    teachers = execute_query(f"""
    SELECT teacher_id, name 
    FROM teachers 
    WHERE user_id = {user_id}
    """)
    active_courses = execute_query(f"""
    SELECT active_courses.active_course_id
         , courses.name
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    WHERE teacher_id = {teachers[0][0]}
    """)
    return render_template("attendance.html", active_courses=active_courses, teachers=teachers, message=message)

@app.route('/attendance/<int:active_course_id>', methods=['GET', 'POST'])
def course_attendance(active_course_id):
    current_date = datetime.datetime.now().date().strftime("%Y-%m-%d")
    message = time_message()
    user_id = session['user_id']
    teachers = execute_query(f"""
    SELECT teacher_id, name 
    FROM teachers 
    WHERE user_id = {user_id}
    """)
    active_courses = execute_query(f"""
    SELECT active_courses.active_course_id
         , courses.name
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    WHERE teacher_id = {teachers[0][0]}
    """)
    students = execute_query(f"""
    SELECT
        active_courses.active_course_id,
        students.name,
        students.student_id,
        attendance.status,
        courses.name,
        attendance.attend_date
    FROM active_courses
    JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
    JOIN students ON students_courses.student_id = students.student_id
    LEFT JOIN attendance ON active_courses.active_course_id = attendance.active_course_id 
    AND attendance.attend_date = '{current_date}' AND students.student_id = attendance.student_id
    JOIN courses ON active_courses.course_id = courses.course_id
    WHERE active_courses.active_course_id = {active_course_id}
    """)
    if request.method == 'POST':
        attendance_date = request.form["attendance_date"]
        student_id = request.form['student_id']
        attendance_status = request.form['attendance_status']
        try:
            execute_query(f"""
            INSERT INTO attendance (active_course_id, student_id, status, attend_date)
            VALUES ('{active_course_id}','{student_id}','{attendance_status}','{attendance_date}')
            """)
        except:
            execute_query(f"""
            UPDATE attendance
            SET status = '{attendance_status}'
            WHERE student_id = '{student_id}' AND active_course_id = '{active_course_id}' AND attend_date = '{attendance_date}'
            """)
        return redirect(url_for('course_attendance', active_course_id=active_course_id))
    return render_template("attendance_courses.html", active_courses=active_courses, teachers=teachers, message=message, current_date=current_date, students=students)


@app.route('/show_attendance/', methods=['GET', 'POST'])
def show_attendance():
    message = time_message()
    user_id = session['user_id']
    teachers = execute_query(f"""
    SELECT teacher_id, name 
    FROM teachers 
    WHERE user_id = {user_id}
    """)
    active_courses = execute_query(f"""
    SELECT active_courses.active_course_id, courses.name
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    WHERE teacher_id = {teachers[0][0]}
    """)
    if request.method == 'POST':
        active_course_id = request.form.get('active_course_id')
        attend_dates = execute_query(f"""
        SELECT DISTINCT attend_date
        FROM attendance
        WHERE active_course_id = {active_course_id}
        """)
        course_name = execute_query(f"""
        SELECT courses.name 
        FROM active_courses
        JOIN courses ON active_courses.course_id = courses.course_id
        WHERE active_courses.active_course_id = {active_course_id}
        """)
        if request.form.get('attend_date'):
            attend_date = request.form.get('attend_date')
            attendance = execute_query(f"""
            SELECT attendance.student_id,
            students.name, 
            attendance.status
            FROM attendance
            JOIN students ON attendance.student_id = students.student_id
            WHERE attendance.active_course_id = {active_course_id}
            AND attendance.attend_date = '{attend_date}'
            ORDER BY students.name
            """)
            return render_template("show_attendance.html", attendance=attendance, attend_dates=attend_dates, active_course_id=active_course_id, teachers=teachers, message=message, course_name=course_name, active_courses=active_courses)

        return render_template("show_attendance.html", attend_dates=attend_dates, active_course_id=active_course_id, teachers=teachers, message=message, course_name=course_name)
    
    return render_template("show_attendance.html", active_courses=active_courses, teachers=teachers, message=message)


@app.route('/student_attendance', methods=['POST', 'GET'])
def student_attendance():
    students = execute_query("""
    SELECT DISTINCT 
    students.student_id,
    students.name
    FROM students
    JOIN students_courses ON students.student_id = students_courses.student_id
    JOIN active_courses ON students_courses.active_course_id = active_courses.active_course_id
    JOIN attendance ON active_courses.active_course_id = attendance.active_course_id
    """)
    if 'student' in request.args:
        student = request.args.get("student")
        if student == '':
            return redirect(request.referrer)    
        courses = execute_query(f"""
        SELECT DISTINCT active_courses.active_course_id,
           courses.name,
           students.name,
        students.student_id
        FROM active_courses
        JOIN courses ON active_courses.course_id = courses.course_id
        JOIN attendance ON active_courses.active_course_id = attendance.active_course_id AND students.student_id = attendance.student_id
        JOIN students ON attendance.student_id = students.student_id
        WHERE attendance.student_id = {student}
        """) 
        student_name = courses[0][2]
    else:
        student_name = None
        courses = None
    if request.method == 'POST':
        course = request.form.get("course")
        if course == '':
            return redirect(request.referrer)
        attendance = execute_query(f"""
        SELECT attendance.status,
               attendance.attend_date,
               courses.name,
               active_courses.active_course_id,
               students.name,
               students.student_id
        FROM attendance
        JOIN active_courses ON attendance.active_course_id = active_courses.active_course_id
		JOIN courses ON active_courses.course_id = courses.course_id
        JOIN students ON attendance.student_id = students.student_id
        WHERE active_courses.active_course_id = {course} AND students.student_id = {student}
        """)
        course_name = attendance[0][2]
        student_name = attendance[0][4]

        return render_template("student_attendance.html", students=students, student=student_name, courses=courses, course=course_name, attendance=attendance)
    else:
        course_name = None
        attendance = None
        
    return render_template("student_attendance.html", students=students, student=student_name, courses=courses, course=course_name, attendance=attendance)

###### END PROJECT 2 ######

## TEACHER SEE HIS COURSES ##
@app.route('/teacher/my_courses')
def teacher_my_courses():
    message = time_message()
    user_id = session['user_id']
    teachers = execute_query(f"""
    SELECT teacher_id, name 
    FROM teachers 
    WHERE user_id = {user_id}
    """)
    active_courses = execute_query(f"""
    SELECT active_courses.active_course_id
         , courses.name
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    WHERE teacher_id = {teachers[0][0]}
    """)
    return render_template("teacher_my_courses.html", active_courses=active_courses, teachers=teachers, message=message)

@app.route('/teacher/stats')
def teacher_stats():
    message = time_message()
    user_id = session['user_id']
    teachers = execute_query(f"""
    SELECT teacher_id, name 
    FROM teachers 
    WHERE user_id = {user_id}
    """)
    teacher_id = teachers[0][0]
    course_stats = execute_query(f"""
	SELECT courses.name
          ,COUNT(DISTINCT students_courses.student_id) AS num_students
          ,COUNT(DISTINCT CASE WHEN students.gender = 'Male' THEN students.student_id END) AS num_male_students
          ,COUNT(DISTINCT CASE WHEN students.gender = 'Female' THEN students.student_id END) AS num_female_students
          ,ROUND(AVG(students_courses.grade),2) AS avg_grade
          ,ROUND(AVG((julianday('now') - julianday(students.birth_date)) / 365.25),2) AS avg_age
          ,ROUND(CAST(SUM(CASE WHEN attendance.status = 'YES' THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) AS percent_yes_attendance
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
    JOIN students ON students_courses.student_id = students.student_id
    LEFT JOIN attendance ON attendance.active_course_id = active_courses.active_course_id AND attendance.student_id = students_courses.student_id
    WHERE active_courses.teacher_id = 1
    GROUP BY courses.name
    """)

    stats = execute_query(f"""
    SELECT COUNT(DISTINCT active_courses.course_id) AS num_courses
          ,COUNT(DISTINCT students.student_id) AS num_unique_students
          ,COUNT(CASE WHEN students.gender = 'Male' THEN 1 END) AS num_male_students
          ,COUNT(CASE WHEN students.gender = 'Female' THEN 1 END) AS num_female_students
          ,ROUND(AVG(students_courses.grade),2) AS avg_grade
          ,ROUND(AVG((julianday('now') - julianday(students.birth_date)) / 365.25),2) AS avg_age
          ,ROUND(CAST((SELECT COUNT(*) FROM attendance WHERE status = 'YES' AND active_course_id IN (SELECT active_course_id FROM active_courses WHERE teacher_id = {teacher_id})) AS FLOAT) / (SELECT COUNT(*) FROM attendance WHERE active_course_id IN (SELECT active_course_id FROM active_courses WHERE teacher_id = {teacher_id})), 2) * 100.0 AS attendance_percent
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
    JOIN students ON students_courses.student_id = students.student_id
    WHERE active_courses.teacher_id = {teacher_id}
    """)
    return render_template("teacher_stats.html", stats=stats, course_stats=course_stats, teachers=teachers, message=message)


## STUDENT SEE HIS COURSES ##
@app.route('/my_courses')
def my_courses():
    user_id = session['user_id']
    students = execute_query(f"""
    SELECT student_id, name 
    FROM students 
    WHERE user_id = {user_id}
    """)
    active_courses = execute_query(f"""
    SELECT active_courses.active_course_id
         , courses.name
    FROM active_courses
    JOIN courses ON active_courses.course_id = courses.course_id
    JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
    JOIN students ON students_courses.student_id = students.student_id
    WHERE students.student_id = {students[0][0]}
    """)
    return render_template("my_courses.html", active_courses=active_courses)


@app.route('/course_details/<int:active_course_id>')
def course_details(active_course_id):
    user_id = session['user_id']
    students = execute_query(f"""
    SELECT student_id, name 
    FROM students 
    WHERE user_id = {user_id}
    """)
    # active_courses = execute_query(f"""
    # SELECT active_courses.active_course_id
    #      , courses.name
    # FROM active_courses
    # JOIN courses ON active_courses.course_id = courses.course_id
    # JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
    # JOIN students ON students_courses.student_id = students.student_id
    # WHERE students.student_id = {students[0][0]}
    # """)
    course_details = execute_query(f"""
    SELECT teachers.name
          ,courses.name
          ,active_courses.active_course_id
          ,courses.desc
          ,courses.image
          ,students_courses.grade
          ,courses.syllabus
          ,teachers.phone
          ,users.email
    FROM teachers
    JOIN active_courses ON teachers.teacher_id = active_courses.teacher_id
    JOIN courses ON active_courses.course_id = courses.course_id
    JOIN students_courses ON active_courses.active_course_id = students_courses.active_course_id
    JOIN users ON teachers.user_id = users.user_id
    WHERE active_courses.active_course_id = {active_course_id} AND students_courses.student_id = {students[0][0]}
    """)
    return render_template('my_course_details.html', course_details=course_details)

@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contact-us', methods=['GET', 'POST'])
def contact_form():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        execute_query(f"""
        INSERT INTO contacts (name, email, message) 
        VALUES ('{name}', '{email}', '{message}')
        """)
            
        return render_template('contact-us.html')

    return render_template('contact-us.html')


if __name__ == "__main__":
    app.run(debug=True)