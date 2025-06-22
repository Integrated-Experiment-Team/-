from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from student.forms import StudentRegisterForm
from teacher.forms import TeacherRegisterForm
from django.contrib.auth.views import LoginView, LogoutView
from student.models import StudentProfile
from teacher.models import TeacherProfile

def register(request, user_type):
    # 检查是否使用快速版本
    use_fast = request.GET.get('fast', False)
    template_name = 'register_fast.html' if use_fast else 'register.html'

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

            # 创建用户资料
            try:
                if user_type == 'student':
                    StudentProfile.objects.create(user=user)
                    return redirect('student:student_home')
                elif user_type == 'teacher':
                    TeacherProfile.objects.create(user=user)
                    return redirect('teacher:teacher_home')
            except Exception as e:
                # 如果创建资料失败，注销用户并返回注册页
                from django.contrib.auth import logout
                logout(request)
                return render(request, template_name, {'form': form, 'error': str(e)})
    else:
        if user_type == 'student':
            form = StudentRegisterForm()
        elif user_type == 'teacher':
            form = TeacherRegisterForm()
        else:
            return redirect('login')

    return render(request, template_name, {'form': form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user
        # 判断用户类型
        try:
            if hasattr(user, 'studentprofile'):
                return redirect(reverse('student:student_home'))
            elif hasattr(user, 'teacherprofile'):
                return redirect(reverse('teacher:teacher_home'))
            else:
                # 如果没有找到用户类型，重定向到登录页
                return redirect('login')
        except Exception as e:
            # 如果发生任何错误，重定向到登录页
            return redirect('login')

class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        # 执行登出操作
        logout(request)
        # 重定向到登录页面
        return redirect('login')

def student_success(request):
    return render(request, 'student_success.html')
