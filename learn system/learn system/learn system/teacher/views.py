from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseCreateForm, TeacherInfoForm
from .models import TeacherProfile, Course

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
    
    # 查询该教师所创建的所有课程
    courses = Course.objects.filter(teacher=teacher_profile)
    
    # 计算统计信息
    total_students = sum(course.students.count() for course in courses)
    total_videos = sum(course.videos.count() for course in courses)
    total_documents = sum(course.documents.count() for course in courses)
    
    # 如果有教师信息，渲染教师主页模板
    return render(request, 'teacher_home.html', {
        'teacher_profile': teacher_profile,
        'courses': courses,
        'total_students': total_students,
        'total_videos': total_videos,
        'total_documents': total_documents,
        'username': request.user.username,
        'user_authenticated': request.user.is_authenticated
    })

@login_required
def teacher_create_profile(request):
    if request.method == 'POST':
        form = TeacherInfoForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('teacher_home')
    else:
        form = TeacherInfoForm()
    return render(request, 'teacher_info.html', {'form': form})

def teacher_course_create(request):
    if request.method == 'POST':
        form = CourseCreateForm(request.POST)
        if form.is_valid():
            course = form.save(request.user)
            # 使用 Django 消息框架传递成功消息
            from django.contrib import messages
            messages.success(request, '课程创建成功！')
            return redirect('teacher:teacher_home')
    else:
        form = CourseCreateForm()
    return render(request, 'teacher_course_create.html', {
        'form': form,
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from .forms import VideoUploadForm, DocumentUploadForm
from .models import Course, Document

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

@login_required
def complete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # 检查课程是否属于当前教师
    teacher_profile = TeacherProfile.objects.get(user=request.user)
    if course.teacher != teacher_profile:
        messages.error(request, '您没有权限完成此课程。')
        return redirect('teacher:teacher_home')
    
    # 可以在这里添加一些额外的课程完成逻辑，比如更新课程状态
    messages.success(request, f'课程 "{course.name}" 创建完成！')
    return redirect('teacher:teacher_home')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ExamCreateForm, QuestionFormSet
from .models import TeacherProfile, Course, Exam, Question  # 添加 Question 模型导入
from django.utils import timezone

@login_required
def create_exam(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    teacher = TeacherProfile.objects.get(user=request.user)
    
    # 检查是否是该课程的教师
    if course.teacher != teacher:
        from django.contrib import messages
        messages.error(request, '您没有权限为此课程创建考试。')
        return redirect('teacher:teacher_home')
    
    if request.method == 'POST':
        exam_form = ExamCreateForm(request.POST)
        question_formset = QuestionFormSet(request.POST)
        
        if exam_form.is_valid() and question_formset.is_valid():
            exam = exam_form.save(commit=False)
            exam.teacher = teacher
            exam.course = course
            exam.save()
            
            # 保存题目
            questions = question_formset.save(commit=False)
            for question in questions:
                question.exam = exam
                question.save()
            
            from django.contrib import messages
            messages.success(request, '考试创建成功！')
            return redirect('teacher:teacher_course_detail', course_id=course.id)
    else:
        exam_form = ExamCreateForm(initial={'course': course})
        question_formset = QuestionFormSet(queryset=Question.objects.none())
    
    return render(request, 'teacher_exam_create.html', {
        'exam_form': exam_form,
        'question_formset': question_formset,
        'course': course
    })

@login_required
def delete_document(request, document_id):
    """删除文档"""
    document = get_object_or_404(Document, id=document_id)
    course = document.course

    # 检查权限：只有课程的教师才能删除文档
    try:
        teacher = TeacherProfile.objects.get(user=request.user)
        if course.teacher != teacher:
            messages.error(request, '您没有权限删除此文档。')
            return redirect('teacher:teacher_course_detail', course_id=course.id)
    except TeacherProfile.DoesNotExist:
        messages.error(request, '您没有教师权限。')
        return redirect('teacher:teacher_home')

    if request.method == 'POST':
        # 删除文件
        if document.file:
            try:
                document.file.delete()
            except:
                pass  # 如果文件删除失败，继续删除数据库记录

        # 删除数据库记录
        document_name = document.name
        document.delete()

        messages.success(request, f'文档 "{document_name}" 已成功删除。')
        return redirect('teacher:teacher_course_detail', course_id=course.id)

    # 如果是GET请求，返回确认页面或直接删除（根据需要）
    return redirect('teacher:teacher_course_detail', course_id=course.id)