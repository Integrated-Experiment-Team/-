from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.urls import reverse_lazy, reverse
from student.forms import StudentRegisterForm
from teacher.forms import TeacherRegisterForm
from django.contrib.auth.views import LoginView
from student.models import StudentProfile
from teacher.models import TeacherProfile

def register(request, user_type):
    if request.method == 'POST':
        if user_type == 'student':
            form = StudentRegisterForm(request.POST)
        elif user_type == 'teacher':
            form = TeacherRegisterForm(request.POST)
        else:
            return redirect('login')
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
    else:
        if user_type == 'student':
            form = StudentRegisterForm()
        elif user_type == 'teacher':
            form = TeacherRegisterForm()
        else:
            return redirect('login')
    return render(request, 'register.html', {'form': form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        # 判断用户类型
        if hasattr(user, 'studentprofile'):
            return redirect(reverse('student_home'))
        elif hasattr(user, 'teacherprofile'):
            return redirect(reverse('teacher_home'))
        else:
            # 默认跳转到登录页或报错
            return redirect('login')
