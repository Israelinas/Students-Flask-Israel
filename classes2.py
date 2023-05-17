from setup_db import query

class Student():
    def __init__(self, student) -> None:
        self.id = student[0]
        self.user_id = student[1]
        self.name = student[2]
        self.email = student[3]
        self.password = student[4]

    def __str__(self) -> str:
        return self.name



class Teacher():
    def __init__(self, teacher) -> None:
        self.id = teacher[0]
        self.name = teacher[1]
        self.user_id = teacher[2]
        self.email = teacher[3]
        self.password = teacher[4]

    def __str__(self) -> str:
        return self.name


class Course():
    def __init__(self, course) -> None:
        self.id = course[0]
        self.name = course[1]
        self.desc = course[2]

    def __str__(self) -> str:
        return self.name

class CourseNum():
    def __init__(self, course) -> None:
        self.id = course[0]
        self.course_id=course[1]
        self.start_date=course[2]
        self.end_date=course[3]
        self.teacher_id=course[4]
        self.name=course[5]
    
    def __str__(self) -> str:
        return self.name
        