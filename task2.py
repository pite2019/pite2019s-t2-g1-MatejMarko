class Student:
	
	def __init__(self, name, surname, classes):
		self.name = name
		self.surname = surname
		self.classes = classes

	def getName(self):
		print("Student: " + self.name + " " + self.surname) 

	def averageByClass(self, name):
		for i in range(len(self.classes)):
			if self.classes[i].name == name:
				print("Average grade for " + self.classes[i].name + " is " + repr(self.getAverageGrade(self.classes[i].grades)))
			
	def getAverageGrade(self, grades):
		return sum(grades) / len(grades)

class Class:

	def __init__(self, name, grades):
		self.name = name
		self.grades = grades


c1 = Class("Math", [4,5,3,4])
c2 = Class("English", [5,5,4,4])
c3 = Class("Science", [2,5,4,4])
c4 = Class("Technology", [2,5,5,4])
s = Student("Matej", "Marko", [c1, c2, c3, c4])
s.getName()
s.averageByClass("Math")
s.averageByClass("English")
s.averageByClass("Science")
s.averageByClass("Technology")
