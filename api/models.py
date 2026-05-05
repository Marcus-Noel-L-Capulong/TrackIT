from django.db import models

class User(models.Model):
    user_id = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=100)
    
    ROLE_CHOICES = [
        ('Admin', 'Admin'), 
        ('Instructor', 'Instructor'), 
        ('Student', 'Student')
    ]
    role = models.CharField(max_length=15, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Course(models.Model):
    course_id = models.CharField(max_length=20, primary_key=True)
    course_name = models.CharField(max_length=100)
    # Instructor is a User filtered by the 'Instructor' role
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Instructor'})

    def __str__(self):
        return f"{self.course_id}: {self.course_name}"


class AttendanceRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    date = models.DateField()
    
    STATUS_CHOICES = [
        ('Present', 'Present'), 
        ('Absent', 'Absent'), 
        ('Late', 'Late')
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    
    # Student is a User filtered by the 'Student' role
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.name} | {self.course.course_id} | {self.date} | {self.status}"