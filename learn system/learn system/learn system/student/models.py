from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, verbose_name='姓名')
    student_id = models.CharField(max_length=20, unique=True, verbose_name='学号')
    college = models.CharField(max_length=50, verbose_name='学院')
    contact = models.CharField(max_length=50, verbose_name='联系方式')

    def __str__(self):
        return self.name

class ExamResult(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='exam_results', verbose_name='学生')
    exam = models.ForeignKey('teacher.Exam', on_delete=models.CASCADE, related_name='results', verbose_name='考试')
    score = models.IntegerField(verbose_name='得分')
    submitted_at = models.DateTimeField(default=timezone.now, verbose_name='提交时间')
    selected_options = models.JSONField(verbose_name='选择的答案')

    class Meta:
        unique_together = ['student', 'exam']

    def __str__(self):
        return f"{self.student.name} - {self.exam.name} - {self.score}分"
