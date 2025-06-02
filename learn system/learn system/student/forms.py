from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import StudentProfile

class StudentRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50, label='姓名')
    student_id = forms.CharField(max_length=20, label='学号')
    college = forms.CharField(max_length=50, label='学院')
    contact = forms.CharField(max_length=50, label='联系方式')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'student_id', 'college', 'contact')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username'] + '@example.com'
        if commit:
            user.save()
            student_profile = StudentProfile.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                student_id=self.cleaned_data['student_id'],
                college=self.cleaned_data['college'],
                contact=self.cleaned_data['contact']
            )
            student_profile.save()
        return user


from django import forms
from teacher.models import Course

class CourseSearchForm(forms.Form):
    keyword = forms.CharField(max_length=50, label='搜索', required=False)

    def search(self):
        keyword = self.cleaned_data['keyword']
        if keyword:
            courses = Course.objects.filter(name__icontains=keyword)
        else:
            courses = Course.objects.all()
        return courses



from django import forms
from teacher.models import Course
from .models import StudentProfile

class CourseSelectionForm(forms.Form):
    course_id = forms.IntegerField(widget=forms.HiddenInput())

    def select(self, user):
        course_id = self.cleaned_data['course_id']
        course = Course.objects.get(id=course_id)
        student_profile = StudentProfile.objects.get(user=user)
        student_profile.courses.add(course)
        return course
