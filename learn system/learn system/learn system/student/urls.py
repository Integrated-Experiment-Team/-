from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/student/', views.student_register, name='student_register'),
    path('home/', views.student_home, name='student_home'),
    path('course/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    path('info/', views.student_info, name='student_info'),
    path('profile/edit/', views.student_profile_edit, name='student_profile_edit'),

    # 新增的考试相关URL
    path('exams/', views.exam_list, name='student_exam_list'),
    path('exam/<int:exam_id>/', views.exam_detail, name='student_exam_detail'),
]

