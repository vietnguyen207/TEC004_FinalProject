from abc import ABC, abstractmethod

# -------------------
# PERSON
# -------------------

class Person(ABC):

    def __init__(self,id,name,email):
        self.id = id
        self.name = name
        self.email = email


class Student(Person):

    def __init__(self,id,name,email,major):
        super().__init__(id,name,email)
        self.major = major


class Instructor(Person):

    def __init__(self,id,name,email,department):
        super().__init__(id,name,email)
        self.department = department


# -------------------
# COURSE
# -------------------

class Course:

    def __init__(self,id,name,credits,semester,sessions):
        self.id = id
        self.name = name
        self.credits = credits
        self.semester = semester
        self.sessions = sessions


# -------------------
# GRADING SCHEME
# -------------------

class GradingScheme(ABC):

    @abstractmethod
    def calculate_grade(self):
        pass


class WeightedGrading(GradingScheme):

    def __init__(self,assignment,midterm,final):

        self.assignment = float(assignment)
        self.midterm = float(midterm)
        self.final = float(final)

    def calculate_grade(self):

        return (
            self.assignment * 0.3
            + self.midterm * 0.3
            + self.final * 0.4
        )

