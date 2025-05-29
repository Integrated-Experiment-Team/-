from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseCreateForm
from .models import TeacherProfile

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import TeacherProfile

@login_required
def teacher_home(request):
    try:
        teacher_profile = TeacherProfile.objects.get(user=request.user)
    except TeacherProfile.DoesNotExist:
        # 如果没有教师信息，重定向到创建教师信息的页面
        return redirect('teacher_create_profile')
    # 如果有教师信息，渲染教师主页模板
    return render(request, 'teacher_home.html', {'teacher_profile': teacher_profile})


def teacher_course_create(request):
    if request.method == 'POST':
        form = CourseCreateForm(request.POST)
        if form.is_valid():
            course = form.save(request.user)
            return redirect('teacher_course_detail', course.id)
    else:
        form = CourseCreateForm()
    return render(request, 'teacher_course_create.html', {
        'form': form,
    })


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import VideoUploadForm, DocumentUploadForm
from .models import Course

def teacher_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        if 'video' in request.POST:
            video_form = VideoUploadForm(request.POST, request.FILES)
            document_form = DocumentUploadForm()
            if video_form.is_valid():
                video = video_form.save(course)
                return render(request, 'teacher_course_detail.html', {
                    'video_form': video_form,
                    'document_form': document_form,
                    'course': course,
                    'message': '你已成功上传了视频文件！'
                })
        elif 'document' in request.POST:
            video_form = VideoUploadForm()
            document_form = DocumentUploadForm(request.POST, request.FILES)
            if document_form.is_valid():
                document = document_form.save(course)
                return render(request, 'teacher_course_detail.html', {
                    'video_form': video_form,
                    'document_form': document_form,
                    'course': course,
                    'message': '你已成功上传了文档文件！'
                })
    else:
        video_form = VideoUploadForm()
        document_form = DocumentUploadForm()
    return render(request, 'teacher_course_detail.html', {
        'video_form': video_form,
        'document_form': document_form,
        'course': course,
    })


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import TeacherInfoForm
from .models import TeacherProfile

def admin_home(request):
    if request.method == 'POST':
        teacher_id = request.POST.get('teacher_id')
        teacher_profile = get_object_or_404(TeacherProfile, id=teacher_id)
        form = TeacherInfoForm(request.POST, instance=teacher_profile)
        if form.is_valid():
            form.save()
            return render(request, 'admin_home.html', {
                'form': form,
                'teachers': TeacherProfile.objects.all(),
                'message': '你已成功修改了老师信息！'
            })
    else:
        form = TeacherInfoForm()
    return render(request, 'admin_home.html', {
        'form': form,
        'teachers': TeacherProfile.objects.all(),
    })

def teacher_profile(request):
    pass