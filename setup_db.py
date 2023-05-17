import sqlite3


with sqlite3.connect("database.db", check_same_thread=False) as conn:
    cur = conn.cursor()


def execute_query(schema):
    cur.execute(schema)
    conn.commit()
    return cur.fetchall()


def executemany_query(schema, value):
    cur.executemany(schema, value)
    conn.commit()
    return cur.fetchall()


def create_tables():
    execute_query("""
        CREATE TABLE IF NOT EXISTS subscribers (
            subscriber_id             INTEGER     PRIMARY KEY
          , email                     TEXT        NOT NULL        UNIQUE
        )
    """)

    execute_query("""
        CREATE TABLE IF NOT EXISTS leads (
            lead_id                   INTEGER     PRIMARY KEY
          , name                      TEXT        NOT NULL
          , phone                     TEXT        NOT NULL
          , email                     TEXT        NOT NULL
          , city                      TEXT                
          , status                    TEXT        
        )
    """)


    execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id                   INTEGER     PRIMARY KEY
          , role                      TEXT        NOT NULL
          , email                     TEXT        NOT NULL        UNIQUE
          , password                  TEXT        NOT NULL
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS students (
            student_id                INTEGER     PRIMARY KEY
          , user_id                   INTEGER     NOT NULL        UNIQUE
          , name                      TEXT        NOT NULL
          , image                     TEXT        NOT NULL
          , gender                    TEXT        NOT NULL
          , birth_date                TEXT        NOT NULL
          , phone                     TEXT        NOT NULL
          , address                   TEXT        NOT NULL
          , FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id                INTEGER     PRIMARY KEY
          , user_id                   INTEGER     NOT NULL        UNIQUE
          , name                      TEXT        NOT NULL
          , image                     TEXT        NOT NULL
          , gender                    TEXT        NOT NULL
          , birth_date                TEXT        NOT NULL
          , phone                     TEXT        NOT NULL
          , address                   TEXT        NOT NULL
          , FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id                 INTEGER     PRIMARY KEY
          , name                      TEXT        NOT NULL        UNIQUE
          , desc                      TEXT        NOT NULL
          , image                     TEXT        
          , syllabus                  TEXT        
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS active_courses (
            active_course_id          INTEGER     PRIMARY KEY
          , course_id                 INTEGER     NOT NULL
          , teacher_id                INTEGER     NOT NULL
          , start_date                DATE        NOT NULL
          , end_date                  DATE        NOT NULL
          , FOREIGN KEY (course_id)   REFERENCES courses (course_id)
          , FOREIGN KEY (teacher_id)  REFERENCES teachers (teacher_id)
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS students_courses (
            students_courses_id       INTEGER     PRIMARY KEY
          , active_course_id          INTEGER     NOT NULL
          , student_id                INTEGER     NOT NULL
          , grade                     INTEGER
          , FOREIGN KEY (active_course_id) REFERENCES active_courses (active_course_id)
          , FOREIGN KEY (student_id) REFERENCES students (student_id)
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id             INTEGER     PRIMARY KEY
          , active_course_id          INTEGER     NOT NULL
          , student_id                INTEGER     NOT NULL
          , status                    TEXT
          , attend_date               DATE
          , FOREIGN KEY (active_course_id) REFERENCES active_courses (active_course_id)
          , FOREIGN KEY (student_id) REFERENCES students (student_id)
          , UNIQUE (active_course_id, student_id, attend_date)
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id                INTEGER     PRIMARY KEY
          , message                   TEXT        NOT NULL
        )
        """)
    execute_query("""
        CREATE TABLE IF NOT EXISTS contacts (
            contact_id                INTEGER     PRIMARY KEY
          , name                      TEXT        NOT NULL
          , email                     TEXT        NOT NULL
          , message                   TEXT        NOT NULL
        )
        """)


def add_admin_user():
    execute_query("""
        INSERT INTO users (role, email, password)
        VALUES ('Admin', 'admin@admin.com', 'admin')
        """)


if __name__ == "__main__":
    create_tables()
    add_admin_user()
