from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from student.models import StudentProfile

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='姓名')
    teacher_id = models.CharField(max_length=20, unique=True, verbose_name='工号')
    college = models.CharField(max_length=50, verbose_name='学院')
    contact = models.CharField(max_length=50, verbose_name='联系方式')

    def __str__(self):
        return self.name


from django.db import models
from student.models import StudentProfile
from .models import TeacherProfile

class Course(models.Model):
    name = models.CharField(max_length=50, verbose_name='课程名称')
    description = models.TextField(verbose_name='课程描述')
    code = models.CharField(max_length=20, unique=True, verbose_name='课程标识')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='courses', verbose_name='老师')
    students = models.ManyToManyField(StudentProfile, related_name='courses', verbose_name='学生')

    def __str__(self):
        return self.name


from django.db import models
from django.utils import timezone

class Video(models.Model):
    name = models.CharField(max_length=50, verbose_name='文件名')
    file = models.FileField(upload_to='media/', verbose_name='文件路径')
    upload_time = models.DateTimeField(default=timezone.now, verbose_name='上传时间')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='videos', verbose_name='课程')

    def __str__(self):
        return self.name

class Document(models.Model):
    name = models.CharField(max_length=50, verbose_name='文件名')
    file = models.FileField(upload_to='media/', verbose_name='文件路径')
    upload_time = models.DateTimeField(default=timezone.now, verbose_name='上传时间')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='documents', verbose_name='课程')

    def __str__(self):
        return self.name

class Exam(models.Model):
    name = models.CharField(max_length=100, verbose_name='考试名称')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams', verbose_name='关联课程')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='exams', verbose_name='出题老师')
    release_time = models.DateTimeField(default=timezone.now, verbose_name='发布时间')
    deadline = models.DateTimeField(verbose_name='截止时间')
    total_score = models.IntegerField(default=100, verbose_name='总分')

    def __str__(self):
        return f"{self.name} - {self.course.name}"

class Question(models.Model):
    QUESTION_TYPES = [
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions', verbose_name='所属考试')
    text = models.TextField(verbose_name='题目')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single_choice', verbose_name='题目类型')
    options = models.JSONField(verbose_name='选项')
    correct_options = models.JSONField(verbose_name='正确答案')
    points = models.IntegerField(default=5, verbose_name='分值')

    def __str__(self):
        return f"{self.text[:50]} - {self.exam.name}"
