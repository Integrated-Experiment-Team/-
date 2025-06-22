from django.urls import path
from .views import (
    teacher_home,
    teacher_course_create,
    teacher_course_detail,
    admin_home,
    teacher_create_profile,
    create_exam,  # 添加这个导入
    delete_document  # 添加删除文档的导入
)

app_name = 'teacher'

urlpatterns = [
    path('home/', teacher_home, name='teacher_home'),
    path('profile/create/', teacher_create_profile, name='teacher_create_profile'),
    path('course/create/', teacher_course_create, name='teacher_course_create'),
    path('course/<int:course_id>/', teacher_course_detail, name='teacher_course_detail'),
    # 添加创建考试的 URL
    path('course/<int:course_id>/exam/create/', create_exam, name='create_exam'),
    # 添加删除文档的 URL
    path('document/<int:document_id>/delete/', delete_document, name='delete_document'),
    path('admin/', admin_home, name='admin_home'),
]
