from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeacherProfile
from django.forms import modelformset_factory
from django.utils import timezone

class TeacherRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=50, label='姓名')
    teacher_id = forms.CharField(max_length=20, label='工号')
    college = forms.CharField(max_length=50, label='学院')
    contact = forms.CharField(max_length=50, label='联系方式')

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'teacher_id', 'college', 'contact')

    def clean_teacher_id(self):
        teacher_id = self.cleaned_data['teacher_id']
        if TeacherProfile.objects.filter(teacher_id=teacher_id).exists():
            raise forms.ValidationError('该工号已被注册，请更换工号。')
        return teacher_id

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

from django import forms
from .models import Video, Document, Exam, Question, Course

class ExamCreateForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['name', 'deadline', 'total_score']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入考试名称'}),
            'total_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
        }
        labels = {
            'name': '考试名称',
            'deadline': '截止时间',
            'total_score': '总分',
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 2:
            raise forms.ValidationError('考试名称至少需要2个字符')
        return name

    def clean_deadline(self):
        deadline = self.cleaned_data['deadline']
        if deadline <= timezone.now():
            raise forms.ValidationError('截止时间必须晚于当前时间')
        return deadline

    def clean_total_score(self):
        total_score = self.cleaned_data['total_score']
        if total_score < 1 or total_score > 100:
            raise forms.ValidationError('总分必须在1到100之间')
        return total_score

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'options', 'correct_options', 'points']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入题目'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'options': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': '每个选项占一行'}),
            'correct_options': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': '正确答案'}),
            'points': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 20}),
        }
        labels = {
            'text': '题目内容',
            'question_type': '题目类型',
            'options': '选项（每行一个）',
            'correct_options': '正确答案',
            'points': '分值',
        }

    def clean_text(self):
        text = self.cleaned_data['text']
        if len(text) < 2:
            raise forms.ValidationError('题目内容至少需要2个字符')
        return text

    def clean_options(self):
        options = self.cleaned_data['options']
        
        # 如果已经是列表，直接返回
        if isinstance(options, list):
            if len(options) < 2:
                raise forms.ValidationError('至少需要2个选项')
            return options
        
        # 如果是字符串，按换行符分割
        if not options or len(options.split('\n')) < 2:
            raise forms.ValidationError('至少需要2个选项')
        return options.split('\n')

    def clean_correct_options(self):
        correct_options = self.cleaned_data.get('correct_options', '')
        question_type = self.cleaned_data.get('question_type')
        
        # 如果已经是列表，直接使用
        if isinstance(correct_options, list):
            if not correct_options:
                raise forms.ValidationError('请选择正确答案')
            
            if question_type == 'single_choice' and len(correct_options) > 1:
                raise forms.ValidationError('单选题只能有一个正确答案')
            
            return correct_options
        
        # 如果是字符串，按换行符分割
        if not correct_options:
            raise forms.ValidationError('请选择正确答案')
        
        correct_options = correct_options.split('\n')
        
        if question_type == 'single_choice' and len(correct_options) > 1:
            raise forms.ValidationError('单选题只能有一个正确答案')
        
        return correct_options

    def clean_points(self):
        points = self.cleaned_data['points']
        if points < 1 or points > 20:
            raise forms.ValidationError('分值必须在1到20之间')
        return points

QuestionFormSet = modelformset_factory(
    Question, 
    form=QuestionForm, 
    extra=3,  # 默认显示3个空白表单
    can_delete=True,
    min_num=1,  # 至少需要1个题目
    validate_min=True
)
