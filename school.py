import json
import random
import re
import os

STUDENTS_FILE = 'all_students.json'
CLASSES_FILE = 'classes.json'

list_of_all_students = None


class Student:

    def __init__(self, first_name, last_name, birth_date, email_address, student_id=None, classes=[], add=True):

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.email_address = email_address
        self.student_id = student_id
        self.classes = classes

        if add:
            self.add_student(STUDENTS_FILE)

    def __getitem__(self, key):
        return getattr(self, key)

    def __str__(self):
        return self.student_id + ": " + self.first_name + ' ' + self.last_name

    def add_student(self, file_path):

        emails_list = []
        student_ids = []
        students = get_from_json_file(file_path)
        for p in students:
            emails_list.append(p['email_address'])
            student_ids.append(p['student_id'])

        valid_email = validate_email(emails_list, self.email_address)
        if valid_email:
            self.student_id = generate_student_id()
            while self.student_id in student_ids:
                self.student_id = generate_student_id()

            list_of_all_students.append(self)
            students.append(self.__dict__)
            add_to_file(file_path, students)
            print('Addes student with id: ' + self.student_id)
        else:
            print('Invalid email address')

    def add_class(self, code):
        already_assigned = False
        for c in self.classes:
            if c['code'] == code:
                already_assigned = True
        if not already_assigned:
            classes_from_file = get_from_json_file(CLASSES_FILE)
            exists = False
            for c in classes_from_file:
                if c['code'] == code:
                    exists = True
            if exists:
                student_class = StudentsClass(code)
                self.classes.append(student_class.__dict__)
                update_students_file(self)

    def add_grade(self, code, grade):
        for c in self.classes:
            if c['code'] == code:
                grades = c['grades']
                grades.append(grade)
                c['grades'] = grades
                update_students_file(self)

    def set_attendance(self, code, present):
        for c in self.classes:
            if c['code'] == code:
                presence = c['presence']
                presence.append(present)
                c['presence'] = presence
                update_students_file(self)

    def get_student_average(self):
        grades_total = 0
        nr_of_grades = 0
        for c in self.classes:
            grades_total += sum(c['grades'])
            nr_of_grades += len(c['grades'])

        if nr_of_grades != 0:
            average_grade = grades_total / nr_of_grades
            return 'Student ' + self.first_name + ' ' + self.last_name + ' has an average of ' + str(average_grade)

        return 'Student ' + self.first_name + ' ' + self.last_name + ' has no grades so far'

    def get_student_class_average(self, code):
        for c in self.classes:
            if c['code'] == code and len(c['grades']) != 0:
                average_grade = sum(c['grades']) / len(c['grades'])
                return 'Student ' + self.first_name + ' ' + self.last_name + ' has an average of ' + \
                       str(average_grade) + ' at class ' + code
        return 'Student ' + self.first_name + ' ' + self.last_name + ' is not assigned to class with code ' + code + \
               ' or has not received any grade so far'

    def get_student_general_attendance(self):
        present = 0
        nr_of_classes = 0
        for c in self.classes:
            present += sum(c['presence'])
            nr_of_classes += len(c['presence'])
        if nr_of_classes != 0:
            presence = (present / nr_of_classes) * 100
            return 'Student ' + self.first_name + ' ' + self.last_name + ' has attended ' + \
                   str(present) + ' out of ' + str(nr_of_classes) + \
                   ' classes, which equals to ' + str(presence) + "%"
        return 'Student ' + self.first_name + ' ' + self.last_name + ' is not assgined to any class.'

    def get_student_class_attendance(self, code):
        for c in self.classes:
            if c['code'] == code and len(c['presence']) != 0:
                presence = sum(c['presence']) / len(c['presence']) * 100
                return 'Student ' + self.first_name + ' ' + self.last_name + ' has attended ' + \
                       str(sum(c['presence'])) + ' out of ' + str(len(c['presence'])) + ' ' + code + \
                       ' classes, which equals to ' + str(presence) + "%"
        return 'Student ' + self.first_name + ' ' + self.last_name + ' is not assigned to class with code ' + code


def generate_student_id():
    id_number = 'E' + str(random.randint(1, 9))
    for digit in range(6):
        id_number += str(random.randint(0, 9))
    return id_number


def get_student_by_id(s_id):
    selected_student = list(filter(lambda x: x.student_id == s_id, list_of_all_students))
    if len(selected_student) != 0:
        return list(filter(lambda x: x.student_id == s_id, list_of_all_students))[0]
    else:
        return None


def validate_email(emails_list, email):
    pattern = re.compile("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if pattern.match(email) and email not in emails_list:
        return True
    else:
        return False


def set_student_from_dict(student_dict):
    name = student_dict['first_name']
    surname = student_dict['last_name']
    birth_date = student_dict['birth_date']
    email_address = student_dict['email_address']
    student_id = student_dict['student_id']
    classes = student_dict['classes']
    return Student(name, surname, birth_date, email_address, student_id, classes, add=False)


class Class:

    def __init__(self, name, ects, code, add=True):
        self.name = name
        self.ects = ects
        self.code = code

        if add:
            self.add_class()

    def add_class(self):
        class_codes = []
        all_classes = get_from_json_file(CLASSES_FILE)
        for c in all_classes:
            class_codes.append(c['code'])

        if self.code not in class_codes:
            all_classes.append(self.__dict__)
            add_to_file(CLASSES_FILE, all_classes)


def update_class(code, new_class_info):
    classes = get_from_json_file(CLASSES_FILE)
    for index, c in enumerate(classes):
        if c['code'] == code:
            classes[index] = new_class_info
    classes = json.loads(json.dumps(classes, default=lambda x: x.__dict__))
    add_to_file(CLASSES_FILE, classes)


def get_class_average(code):
    grades_total = 0
    nr_of_grades = 0
    for student_ in list_of_all_students:
        for class_ in student_['classes']:
            if class_['code'] == code:
                grades_total += sum(class_['grades'])
                nr_of_grades += len(class_['grades'])

    if nr_of_grades != 0:
        average = grades_total / nr_of_grades
        return 'Average grade of class ' + code + ' is ' + str(average)

    return 'There are no grades assigned yet for course ' + code + ' or the course does not exist'


def get_class_attendance(code):
    total_attendances = 0
    number_of_classes = 0
    for student_ in list_of_all_students:
        for class_ in student_['classes']:
            if class_['code'] == code:
                total_attendances += sum(class_['presence'])
                number_of_classes += len(class_['presence'])

    if number_of_classes != 0:
        average = total_attendances / number_of_classes * 100
        return 'Attendance of class ' + code + ' is ' + str(total_attendances) + ' out of ' + str(number_of_classes) \
               + ' which equals to ' + str(average) + '%'

    return 'There were no ' + code + ' classes so far or the course does not exist'


class StudentsClass:

    def __init__(self, class_code):
        self.code = class_code
        self.grades = []
        self.presence = []


def get_from_json_file(file_path):
    if os.stat(file_path).st_size == 0:
        with open(file_path, 'w') as outfile:
            json.dump([], outfile)

    with open(file_path) as file:
        return json.load(file)


def add_to_file(file_path, students):
    with open(file_path, 'w') as outfile:
        json.dump(students, outfile)


def update_students_file(updated_student):
    for index, s in enumerate(list_of_all_students):
        if s.student_id == updated_student.student_id:
            list_of_all_students[index] = updated_student

    json_students = json.loads(json.dumps(list_of_all_students, default=lambda x: x.__dict__))
    add_to_file(STUDENTS_FILE, json_students)


if __name__ == '__main__':

    students_list = get_from_json_file(STUDENTS_FILE)
    list_of_all_students = []
    for i in students_list:
        student = set_student_from_dict(i)
        list_of_all_students.append(student)

    print('School system')
    options = 'Enter a number to execute desired action\n' \
              '1 - Get list of students\n' \
              '2 - Get list of students\n' \
              '3 - Get student average\n' \
              '4 - Get student average by class\n' \
              '5 - Get student attendance\n' \
              '6 - Get student attendance by class\n' \
              '7 - Get class average\n' \
              '8 - Get class attendance\n' \
              '9 - Add student\n' \
              '10 - Add class to student\n' \
              '11 - Add grade to student\n' \
              '12 - Set attendance to student\n' \
              '13 - Exit program'

    action = 0
    while action != 13:
        print(options + '\n')

        action = input('What would you like to get: ')
        print()

        if action == '1':
            print('List of students:')
            for stud in list_of_all_students:
                print(stud)

        elif action == '2':
            print('List of classes:')
            classes = get_from_json_file(CLASSES_FILE)
            for c in classes:
                print(c['name'] + ' (' + c['code'] + ')')

        elif action == '3':
            print('Getting student average')
            student_id = input('Student id: ')
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                print(s.get_student_average())

        elif action == '4':
            print('Getting student average by class')
            student_id = input('Student id: ')
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                class_code = input('Class code: ')
                avg = s.get_student_class_average(class_code)
                print(avg)

        elif action == '5':
            print('Getting student attendance')
            student_id = input('Student id: ')
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                print(s.get_student_general_attendance())

        elif action == '6':
            print('Getting student attendance by class')
            student_id = input('Student id: ')
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                class_code = input('Class code: ')
                avg = s.get_student_class_attendance(class_code)
                print(avg)

        elif action == '7':
            print('Getting class average')
            class_code = input('Class code: ')
            print(get_class_average(class_code))

        elif action == '8':
            print('Getting class attendance')
            class_code = input('Class code: ')
            print(get_class_attendance(class_code))

        elif action == '9':
            print('Adding new student')
            first_name = input('First name: ')
            last_name = input('Last name: ')
            birth_date = input('Birth date: ')
            email = input('Email: ')
            Student(first_name, last_name, birth_date, email)

        elif action == '10':
            print('Adding class to student')
            student_id = input('Student id: ')
            class_code = input('Class code: ')
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                s.add_class(class_code)

        elif action == '11':
            print('Adding grade to student')
            student_id = input('Student id: ')
            class_code = input('Class code: ')
            grade = input('Grade: ')
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                s.add_grade(class_code, int(grade))

        elif action == '12':
            print('Adding attendance to student')
            student_id = input('Student id: ')
            class_code = input('Class code: ')
            grade = input('Did attend (y/n): ')
            did_attend = False
            if grade == 'y':
                did_attend = True
            s = get_student_by_id(student_id)
            if s is None:
                print('Student with such id does not exist')
            else:
                s.set_attendance(class_code, did_attend)

        else:
            action = 13

        print('\n----------------------------------------------------------\n')

    '''
    # EXAMPLE OF USAGE
    students_list = get_from_json_file(STUDENTS_FILE)
    list_of_all_students = []
    for i in students_list:
        student = set_student_from_dict(i)
        list_of_all_students.append(student)
        
    for l in list_of_all_students:
        print(l.get_student_average())
        print(l.get_student_general_attendance())
        print(l.get_student_class_average('pite2019'))
        print(l.get_student_class_attendance('pite2019'))
        print(l.get_student_class_average('ads2019'))
        print(l.get_student_class_attendance('ads2019'))
        print(l.get_student_class_average('math2019'))
        print(l.get_student_class_attendance('math2019'))
        print('------------------------------------------------------------------------------------------------')

    print('------------------------------------------------------------------------------------------------')
    classes_list = get_from_json_file(CLASSES_FILE)
    for c in classes_list:
        print(get_class_average(c['code']))
        print(get_class_attendance(c['code']))
    print('------------------------------------------------------------------------------------------------')
    print('------------------------------------------------------------------------------------------------')


    # creating new student
    id_s = Student('Roger', 'Morrison', '17.10.1994', 'roger@gmail.com')
    roger = get_student_by_id('E8083537')

    roger.add_class('pite2019')
    roger.add_grade('pite2019', 4)
    roger.add_grade('pite2019', 5)
    roger.add_grade('pite2019', 5)
    roger.set_attendance('pite2019', True)
    roger.set_attendance('pite2019', False)
    roger.set_attendance('pite2019', True)
    print(roger.get_student_average())
    print(roger.get_student_general_attendance())
    print(roger.get_student_class_average('pite2019'))
    print(roger.get_student_class_attendance('pite2019'))
    '''
    # update_class('math2019', Class('Math 3', 7, 'math2019', add=False))
