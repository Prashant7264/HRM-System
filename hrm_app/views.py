from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from .models import Department, Role, User
from .forms import DepartmentForm, RoleForm, UserForm, UserLoginForm, ResetPasswordForm, SetNewPasswordForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
import random

otp_storage = {} 

# Create your views here.

def dashboard(request):
    return render(request,'dashboard.html')

def department(request):
    departments = Department.objects.all()
    for department in departments:
        department.status_text = "Active" if department.status else "Inactive"
    return render(request,'department.html',{'departments': departments})

def add_department(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully!")
            return redirect('/department')
    else:
        form = DepartmentForm()
    return render(request, 'add_department.html', {'form': form})

# Update Department View
def update_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, "Department updated successfully!")
            return redirect('/department')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'update_department.html', {'form': form, 'department': department})

# Delete Department (Soft Delete)
def delete_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if request.method == 'POST':
        department.status = False  # Mark as inactive
        department.save()
        messages.warning(request, "Department marked as inactive. Please reassign employees.")
        return redirect('/department')
    return render(request, 'delete_department.html', {'department': department})

def role(request):
    roles = Role.objects.all()
    for role in roles:
        role.status_text = "Active" if role.status else "Inactive"
    return render(request,'role.html',{'roles': roles})

def add_role(request):
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Role added successfully!")
            return redirect('/role')
    else:
        form = RoleForm()
    return render(request, 'add_role.html', {'form': form})

# Update Role View
def update_role(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Role updated successfully!")
            return redirect('/role')
    else:
        form = RoleForm(instance=role)
    return render(request, 'update_role.html', {'form': form, 'role': role})

# Delete Role (Soft Delete)
def delete_role(request, role_id):
    role = get_object_or_404(Role, pk=role_id)
    if request.method == 'POST':
        role.status = False  # Mark as inactive
        role.save()
        messages.warning(request, "Role marked as inactive. Please Change the role of employees.")
        return redirect('/role')
    return render(request, 'delete_role.html', {'role': role})

def employee(request):
    users = User.objects.all()
    # users = User.objects.select_related("role_id", "dept_id").all()
    for user in users:
        
        user.status_text = "Active" if user.is_active else "Inactive"
        
        user.role_name = user.role_id.role_name if user.role_id else "No Role Assigned"
        user.dept_name = user.dept_id.dept_name if user.dept_id else "No Department Assigned"
    return render(request, 'employee.html',{'users': users})

def add_employee(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully!")
            return redirect('/employee')
    else:
        form = UserForm()
    return render(request, 'add_employee.html', {'form': form})

# Update Employee View
def update_employee(request, employee_id):
    user = get_object_or_404(User, pk=employee_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee Details updated successfully!")
            return redirect('/employee')
    else:
        form = UserForm(instance=user)
    return render(request, 'update_employee.html', {'form': form, 'user': user})

# Delete Employee (Soft Delete)
def delete_employee(request, employee_id):
    user = get_object_or_404(User, pk=employee_id)
    if request.method == 'POST':
        user.is_active = False  # Mark as inactive
        user.save()
        messages.warning(request, "Employee marked as inactive.")
        return redirect('/employee')
    return render(request, 'delete_employee.html', {'user': user})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if the user is logging in with the default password
                if user.is_staff and password == 'default_password':  # Replace 'default_password' with actual default
                    # Redirect to password reset page only once
                    return redirect('reset_password')
                else:
                    login(request, user)
                    return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    form_class = ResetPasswordForm
    email_template_name = 'password_reset_email.html'
    success_url = '/login/'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    form_class = SetNewPasswordForm
    success_url = '/login/'



    def send_password_reset_email(user):
        # Generate token and uid
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        # Create reset link
        reset_link = f"{'https' if settings.SECURE_SSL_REDIRECT else 'http'}://{settings.ALLOWED_HOSTS[0]}/reset/{uidb64}/{token}/"

        # Render email template with reset link
        email_content = render_to_string(
            'password_reset_email.html',
            {'reset_link': reset_link, 'user': user}
        )

        # Send email
        send_mail(
            'Password Reset Request',
            email_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
def reset_password(request):
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in after password change
                messages.success(request, 'Your password was successfully updated!')
                return redirect('/dashboard')
            else:
                messages.error(request, 'Please correct the error below.')
        else:
            form = PasswordChangeForm(request.user)
        
        return render(request, 'password_reset.html', {'form': form})
    
def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        email = request.session.get("reset_email")  # Get email from session

        if not email:
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect("request_otp")

        try:
            user = User.objects.get(email=email)  # Fetch user from DB

            # Check if OTP exists and matches
            if email in otp_storage and otp_storage[email] == entered_otp:
                del otp_storage[email]  # Clear OTP after successful verification
                request.session["verified_user"] = user.email  # Store email for password reset
                return redirect("password_reset_confirm")  # Redirect to password reset page
            else:
                messages.error(request, "Invalid OTP. Please try again.")

        except User.DoesNotExist:
            messages.error(request, "User not found. Please request OTP again.")
            return redirect("request_otp")

    return render(request, "enter_otp.html")

def request_otp(request):
    if request.method == "POST":
        email_or_username = request.POST.get("email_or_username")

        # Check if the user exists
        try:
            user = User.objects.get(email=email_or_username) if "@" in email_or_username else User.objects.get(username=email_or_username)
            otp = str(random.randint(100000, 999999))  # Generate 6-digit OTP
            otp_storage[user.email] = otp  # Store OTP temporarily

            # Send OTP via email
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

            request.session["reset_email"] = user.email  # Store email in session
            return redirect("verify_otp")  # Redirect to OTP verification page

        except User.DoesNotExist:
            messages.error(request, "User not found.")
    
    return render(request, "forgot_password.html")


