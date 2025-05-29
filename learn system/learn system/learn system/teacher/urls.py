from django.urls import path
from .views import teacher_home, teacher_course_create, teacher_course_detail, admin_home

urlpatterns = [
    path('teacher_home/', teacher_home, name='teacher_home'),
    path('course/create/', teacher_course_create, name='teacher_course_create'),
    path('course/<int:course_id>/', teacher_course_detail, name='teacher_course_detail'),
    # path('teacher_profile/<int:teacher_id>',teacher_profile,),
    path('admin/', admin_home, name='admin_home'),
]
