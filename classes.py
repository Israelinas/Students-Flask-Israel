from setup_db import execute_query, executemany_query

class Course:
    def __init__(self, id=0) -> None:
        self.id = self.get_data(id, column="course_id")
        self.name = self.get_data(id, column="name")
        self.desc = self.get_data(id, column="desc")
        self.list = self.get_all()

    def get_data(self, id, column):
        try:
            data = execute_query(f"SELECT {column} FROM course WHERE course_id = {id}")
            return data[0][0]
        except:
            pass

    def get_all(self):
        return execute_query("SELECT * FROM course")

    def __str__(self) -> str:
        return self.name


class User:
    def __init__(self) -> None:
        self.id = ""
        self.user_id = ""
        self.name = ""
        self.image = ""
        self.gender = ""
        self.birth_date = ""
        self.phone = ""
        self.address = ""
        self.email = ""
        self.password = ""
    
    def get_data(self, id):
        data = execute_query(f"SELECT ")
        return data[0][0]



class Teacher:
    def __init__(self) -> None:
        pass

class Class():
    def __init__(self) -> None:
        pass

courses = Course()
for c in courses.list:
    print(c)