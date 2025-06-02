from django.urls import path
from .views import student_home, student_course_detail, student_info

urlpatterns = [
    path('student_home/', student_home, name='student_home'),
    path('course/<int:course_id>/', student_course_detail, name='student_course_detail'),
    path('student_info/', student_info, name='student_info'),
]

