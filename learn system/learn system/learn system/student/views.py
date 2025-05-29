from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

from teacher.models import Course
from .forms import CourseSearchForm
from .models import StudentProfile

def student_home(request):
    if request.method == 'POST':
        form = CourseSearchForm(request.POST)
        if form.is_valid():
            courses = form.search()
    else:
        form = CourseSearchForm()
        courses = Course.objects.all()
    student_profile = StudentProfile.objects.get(user=request.user)
    selected_courses = student_profile.courses.all()
    other_courses = courses.exclude(id__in=selected_courses)
    return render(request, 'student_home.html', {
        'form': form,
        'selected_courses': selected_courses,
        'other_courses': other_courses,
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
