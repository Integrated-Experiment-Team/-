from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='姓名')
    student_id = models.CharField(max_length=20, unique=True, verbose_name='学号')
    college = models.CharField(max_length=50, verbose_name='学院')
    contact = models.CharField(max_length=50, verbose_name='联系方式')

    def __str__(self):
        return self.name
