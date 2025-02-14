from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm,  UserCreationForm
from .models import Department, Role, User, PerformanceReview
from django.contrib.auth import get_user_model

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept_name', 'description']
        widgets = {
            'dept_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name', 'description']
        widgets = {
            'role_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email',
            'mobile', 'role', 'department', 'reporting_manager', 'date_of_joining','username','password'
        ]
        widgets = {
            
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(),  # Masked input for passwords
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_joining': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Role"  # Optional: Placeholder for dropdown
    )

    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select Department"  # Optional: Placeholder for dropdown
    )
    reporting_manager = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),  # Optional: Only active users
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        empty_label="Select Reporting Manager"  # Optional: Placeholder for dropdown
    )

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=100, 
        required=True, 
        widget=forms.TextInput(attrs={'placeholder': 'Enter Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter Password'}), 
        required=True
    )

class ResetPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=100, 
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Enter Registered Email'})
    )

class SetNewPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter New Password'}), 
        required=True
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}), 
        required=True
    )

# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = ['task_title', 'task_description','task_priority', 'start_date', 'end_date', 'task_type']

# class TaskAssignmentForm(forms.ModelForm):
#     class Meta:
#         model = TaskAssignment
#         fields = ['task', 'employee', 'status']

class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = ['review_title', 'employee_id','review_date',  'review_period', 'rating', 'comments']
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
            'review_period': forms.Select(choices=PerformanceReview.PERIOD_CHOICES),
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 10}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
