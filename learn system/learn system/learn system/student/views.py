from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import json
from django.contrib.auth import authenticate, login
from django.contrib import messages

from teacher.models import Course, Exam
from .forms import CourseSearchForm, StudentRegisterForm, StudentProfileUpdateForm
from .models import StudentProfile, ExamResult

def index(request):
    return render(request, 'index.html')

def student_register(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 创建学生档案
            StudentProfile.objects.create(
                user=user,
                name=form.cleaned_data.get('username')
            )
            username = form.cleaned_data.get('username')
            messages.success(request, f'账户 {username} 创建成功！')
            return redirect('index')
    else:
        form = StudentRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def student_home(request):
    try:
        student_profile = StudentProfile.objects.get(user=request.user)

        # 获取学生的课程
        selected_courses = student_profile.courses.all()

        # 获取其他可选课程（排除已选课程）
        other_courses = Course.objects.exclude(id__in=selected_courses.values_list('id', flat=True))

        # 获取学生可参加的考试
        current_exams = Exam.objects.filter(
            course__in=selected_courses,
            release_time__lte=timezone.now(),
            deadline__gte=timezone.now()
        )

        # 获取学生的考试成绩
        exam_results = ExamResult.objects.filter(student=student_profile)

        return render(request, 'student_home.html', {
            'student': student_profile,
            'selected_courses': selected_courses,
            'other_courses': other_courses,
            'current_exams': current_exams,
            'exam_results': exam_results,
            'username': request.user.username,
            'user_authenticated': request.user.is_authenticated
        })
    except StudentProfile.DoesNotExist:
        # 如果学生档案不存在，创建一个基本的档案或重定向到创建页面
        # 这里我们显示一个简化的主页，提示用户完善信息
        other_courses = Course.objects.all()

        return render(request, 'student_home.html', {
            'student': None,
            'selected_courses': [],
            'other_courses': other_courses,
            'current_exams': [],
            'exam_results': [],
            'username': request.user.username,
            'user_authenticated': request.user.is_authenticated,
            'error_message': '您的学生档案尚未创建，请联系管理员或完善个人信息。'
        })

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CourseSelectionForm
from teacher.models import Course

def student_course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = CourseSelectionForm(request.POST)
        if form.is_valid():
            course = form.select(request.user)
            return render(request, 'student_course_detail.html', {
                'form': form,
                'course': course,
                'message': '你已成功选择了该课程！'
            })
    else:
        form = CourseSelectionForm(initial={'course_id': course_id})
    return render(request, 'student_course_detail.html', {
        'form': form,
        'course': course,
    })

def student_info(request):
    student_profile = StudentProfile.objects.get(user=request.user)
    return render(request, 'student_info.html', {
        'student': student_profile
    })

@login_required
def student_profile_edit(request):
    """学生信息编辑页面"""
    # 只处理GET请求，显示编辑表单
    # POST请求由前端JavaScript直接调用API处理
    form = StudentProfileUpdateForm()

    return render(request, 'student_profile_edit.html', {
        'form': form,
        'username': request.user.username
    })

def exam_list(request):
    try:
        if request.user.is_authenticated:
            try:
                student = StudentProfile.objects.get(user=request.user)
                # 获取学生所在课程的考试，并且考试在有效期内
                current_time = timezone.now()
                available_exams = Exam.objects.filter(
                    course__in=student.courses.all(),
                    release_time__lte=current_time,
                    deadline__gte=current_time
                )
                # 获取已完成的考试成绩
                completed_results = ExamResult.objects.filter(student=student)
            except StudentProfile.DoesNotExist:
                # 如果没有学生档案，显示所有可用的考试
                current_time = timezone.now()
                available_exams = Exam.objects.filter(
                    release_time__lte=current_time,
                    deadline__gte=current_time
                )
                completed_results = []
        else:
            # 如果没有Django用户登录，显示所有可用的考试
            current_time = timezone.now()
            available_exams = Exam.objects.filter(
                release_time__lte=current_time,
                deadline__gte=current_time
            )

            # 获取session中的临时考试结果
            temp_results = request.session.get('temp_exam_results', [])

            # 创建临时结果对象列表
            completed_results = []
            for result_data in temp_results:
                class TempResult:
                    def __init__(self, data):
                        self.exam = type('obj', (object,), {
                            'id': data['exam_id'],
                            'name': data['exam_name'],
                            'course': type('obj', (object,), {'name': data['course_name']})(),
                            'total_score': data['total_score']
                        })()
                        self.score = data['score']
                        self.submitted_at = data['submitted_at']

                completed_results.append(TempResult(result_data))

        return render(request, 'student_exam_list.html', {
            'exams': available_exams,
            'completed_results': completed_results
        })
    except Exception as e:
        messages.error(request, f'获取考试列表时发生错误: {str(e)}')
        return render(request, 'student_exam_list.html', {
            'exams': [],
            'completed_results': []
        })

def exam_detail(request, exam_id):
    try:
        exam = get_object_or_404(Exam, id=exam_id)

        if request.user.is_authenticated:
            try:
                student = StudentProfile.objects.get(user=request.user)
                # 检查学生是否已经参加过该考试
                existing_result = ExamResult.objects.filter(student=student, exam=exam).first()
                if existing_result:
                    return render(request, 'student_exam_result.html', {'result': existing_result})
            except StudentProfile.DoesNotExist:
                student = None
                existing_result = None
        else:
            student = None
            existing_result = None

        if request.method == 'POST':
            # 处理考试提交
            selected_options = {}
            score = 0

            for question in exam.questions.all():
                selected_option = request.POST.get(f'question_{question.id}')
                selected_options[question.id] = selected_option

                # 计算分数
                if selected_option in question.correct_options:
                    score += question.points

            if student:
                # 如果有Django用户，保存考试结果
                exam_result = ExamResult.objects.create(
                    student=student,
                    exam=exam,
                    score=score,
                    selected_options=json.dumps(selected_options)
                )
                return render(request, 'student_exam_result.html', {'result': exam_result})
            else:
                # 如果没有Django用户，创建临时结果对象用于显示
                from datetime import datetime
                class TempExamResult:
                    def __init__(self, exam, score, selected_options):
                        self.exam = exam
                        self.score = score
                        # 将字典转换为JSON字符串，以便模板过滤器处理
                        self.selected_options = json.dumps(selected_options)
                        self.submitted_at = datetime.now()

                temp_result = TempExamResult(exam, score, selected_options)

                # 将临时结果存储在session中，以便在考试列表中显示
                if 'temp_exam_results' not in request.session:
                    request.session['temp_exam_results'] = []

                # 检查是否已经有这个考试的结果，如果有就更新
                temp_results = request.session['temp_exam_results']
                existing_index = None
                for i, result in enumerate(temp_results):
                    if result['exam_id'] == exam.id:
                        existing_index = i
                        break

                result_data = {
                    'exam_id': exam.id,
                    'exam_name': exam.name,
                    'course_name': exam.course.name,
                    'total_score': exam.total_score,
                    'score': score,
                    'submitted_at': datetime.now().strftime('%Y-%m-%d %H:%M')
                }

                if existing_index is not None:
                    temp_results[existing_index] = result_data
                else:
                    temp_results.append(result_data)

                request.session['temp_exam_results'] = temp_results
                request.session.modified = True

                return render(request, 'student_exam_result.html', {
                    'result': temp_result,
                    'is_temp_result': True
                })

        return render(request, 'student_exam_detail.html', {
            'exam': exam,
            'questions': exam.questions.all(),
            'user_authenticated': request.user.is_authenticated
        })
    except Exception as e:
        messages.error(request, f'访问考试时发生错误: {str(e)}')
        return redirect('student:student_exam_list')
