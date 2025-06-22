"""
URL configuration for course_selection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from .views import register, CustomLoginView, CustomLogoutView, student_success

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/<str:user_type>/', register, name='register'),
    path('register-fast/<str:user_type>/', register, {'fast': True}, name='register_fast'),
    path('student-success/', student_success, name='student_success'),
    path('student/',include('student.urls', namespace='student')),
    path('teacher/',include('teacher.urls', namespace='teacher')),
]

# 在开发环境中提供媒体文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
