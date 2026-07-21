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


class WeightedGrading:

    def __init__(self,
                 assignment,
                 midterm,
                 final,
                 assignment_weight,
                 midterm_weight,
                 final_weight):

        self.assignment = assignment
        self.midterm = midterm
        self.final = final

        self.assignment_weight = assignment_weight
        self.midterm_weight = midterm_weight
        self.final_weight = final_weight

    def calculate_grade(self):

        return (

            self.assignment
            * self.assignment_weight / 100

            +

            self.midterm
            * self.midterm_weight / 100

            +

            self.final
            * self.final_weight / 100

        )

