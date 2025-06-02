from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeacherProfile

class TeacherRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50, label='姓名')
    teacher_id = forms.CharField(max_length=20, label='工号')
    college = forms.CharField(max_length=50, label='学院')
    contact = forms.CharField(max_length=50, label='联系方式')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'teacher_id', 'college', 'contact')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['username'] + '@example.com'
        if commit:
            user.save()
            teacher_profile = TeacherProfile.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                teacher_id=self.cleaned_data['teacher_id'],
                college=self.cleaned_data['college'],
                contact=self.cleaned_data['contact']
            )
            teacher_profile.save()
        return user


from django import forms
from .models import Course

class CourseCreateForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ('name', 'description', 'code')

    def save(self, user, commit=True):
        course = super().save(commit=False)
        course.teacher = user.teacherprofile
        if commit:
            course.save()
        return course


from django import forms
from .models import Video, Document

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('name', 'file')

    def save(self, course, commit=True):
        video = super().save(commit=False)
        video.course = course
        if commit:
            video.save()
        return video

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('name', 'file')

    def save(self, course, commit=True):
        document = super().save(commit=False)
        document.course = course
        if commit:
            document.save()
        return document


from django import forms
from .models import TeacherProfile

class TeacherInfoForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ('name', 'teacher_id', 'college', 'contact')

    def save(self, commit=True):
        teacher_profile = super().save(commit=False)
        if commit:
            teacher_profile.save()
        return teacher_profile
