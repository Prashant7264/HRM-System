from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from .models import Department, Role, User, Task, TaskAssignment
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
from django.contrib.auth.decorators import login_required
import random
from django.utils.dateparse import parse_date
from django.db.models import Q

otp_storage = {} 

# Create your views here.

def dashboard(request):
    is_admin_or_manager = request.user.is_superuser or request.user.groups.filter(name="Manager").exists()
    employees = User.objects.all()  # Fetch all employees for filter dropdown
    tasks = Task.objects.all()  # Start with all tasks

    # Get filter values from GET request
    selected_employee = request.GET.get('employee')
    selected_status = request.GET.get('status')
    selected_start_date = request.GET.get('start_date')
    selected_end_date = request.GET.get('end_date')

    # Apply filters based on user selection
    if selected_employee:
        tasks = tasks.filter(employee_id=selected_employee)

    if selected_status:
        tasks = tasks.filter(task_status=selected_status)

    if selected_start_date:
        tasks = tasks.filter(start_date__gte=selected_start_date)

    if selected_end_date:
        tasks = tasks.filter(end_date__lte=selected_end_date)

    # Task Statistics
    stats = {
        "task_count": tasks.count(),
        "completed": tasks.filter(assignments__status="Completed").count(),
        "in_progress": tasks.filter(assignments__status="In Progress").count(),
        "pending": tasks.filter(assignments__status="Pending").count(),
    }

    context = {
        "employees": employees,
        "tasks": tasks,
        "selected_employee": selected_employee,
        "selected_status": selected_status,
        "selected_start_date": selected_start_date,
        "selected_end_date": selected_end_date,
        "stats": stats
    }

    return render(request, 'dashboard.html', context)

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
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('dashboard')  # Redirect to a logged-in page
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

def create_task(request):
    # Get the current logged-in user (admin, manager, etc.)
    user = request.user

    if request.method == 'POST':
        print(request.POST)
        # Extract data from the form
        title = request.POST.get('task_title')
        description = request.POST.get('task_description')
        priority = request.POST.get('task_priority')
        employee_id = request.POST.get('employee_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        task_type = request.POST.get('task_type')

        # if not title or not description or not priority or not task_type or not start_date or not end_date:
        #     messages.error(request, 'Please fill in all the fields.')
        #     return redirect('/create/') 
        
        # Get the selected employee
        employee = User.objects.get(id=employee_id) if employee_id else None
        
        # Create the Task instance
        task = Task(
            task_title=title,
            task_description=description,
            task_priority=priority,
            start_date=start_date,
            end_date=end_date,
            task_type=task_type,
        )
        task.save()  # Save the task instance first
        
        # Create a TaskAssignment instance
        # task_assignment = TaskAssignment(
        #     task=task,
        #     employee_id=employee,
        #     assigned_by=request.user,  # Current logged-in user is assigning the task
        # )
        # task_assignment.save()  # Save the task assignment
        
        # Show a success message
        messages.success(request, 'Task created and assigned successfully!')
        
        # Redirect to the dashboard or task list page
        return redirect('/dashboard/')
    else:
        # Fetch all employees for the employee dropdown
        employees = User.objects.all()

        # Create an empty task instance for pre-populating the form
        task = Task()

        # Render the form with employees data
        return render(request, 'create_task_form.html', {'employees': employees, 'task': task})

# @login_required
def update_task(request, task_id):
    # Fetch the task to be updated
    task = get_object_or_404(Task, task_id=task_id)

    if request.method == 'POST':
        # Extract data from the form
        title = request.POST.get('task_title')
        description = request.POST.get('task_description')
        priority = request.POST.get('task_priority')
        employee_id = request.POST.get('employee_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        task_type = request.POST.get('task_type')

        # Get the selected employee
        employee = User.objects.get(id=employee_id) if employee_id else None
        
        # Update task instance
        task.task_title = title
        task.task_description = description
        task.task_priority = priority
        task.start_date = start_date
        task.end_date = end_date
        task.task_type = task_type
        task.employee = employee
        task.save()  # Save the updated task instance
        
        # Show success message
        messages.success(request, 'Task updated successfully!')
        
        # Redirect to the dashboard or task list page
        return redirect('/dashboard/')
    
    else:
        # Fetch all employees for the employee dropdown
        employees = User.objects.all()

        # Render the form with existing task data
        return render(request, 'update_task_form.html', {'employees': employees, 'task': task})
    

def delete_task(request, task_id):
    # Fetch the task to be deleted
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        # Delete the task instance
        task.delete()
        
        # Show success message
        messages.success(request, 'Task deleted successfully!')
        
        # Redirect to the dashboard or task list page
        return redirect('/dashboard/')
    
    # Render confirmation template for task deletion
    return render(request, 'confirm_delete.html', {'task': task})


def task_count_view(request):
    # Count the number of tasks (you can filter if needed)
    task_count = Task.objects.count()
    
    # Interpolating count into a string
    message = f'Total number of tasks: {task_count}'
    
    return render(request, 'dashboard.html', {'message': message})

# def task_list(request):
#     # Get filter values from request
#     selected_employee = request.GET.get('employee', '')
#     selected_status = request.GET.get('status', '')
#     selected_start_date = request.GET.get('start_date', '')
#     selected_end_date = request.GET.get('end_date', '')

#     # Fetch tasks
#     tasks = Task.objects.all()

#     # Apply filters
#     if selected_employee:
#         tasks = tasks.filter(employee_id=selected_employee)
    
#     if selected_status:
#         tasks = tasks.filter(task_status=selected_status)

#     if selected_start_date:
#         tasks = tasks.filter(start_date__gte=selected_start_date)

#     if selected_end_date:
#         tasks = tasks.filter(end_date__lte=selected_end_date)

#     # Get employee list for dropdown
#     employees = User.objects.all()

#     # Task statistics
#     stats = {
#         'task_count': tasks.count(),
#         'completed': tasks.filter(task_status='Completed').count(),
#         'in_progress': tasks.filter(task_status='In Progress').count(),
#         'pending': tasks.filter(task_status='Pending').count(),
#     }

#     context = {
#         'tasks': tasks,
#         'employees': employees,
#         'selected_employee': selected_employee,
#         'selected_status': selected_status,
#         'selected_start_date': selected_start_date,
#         'selected_end_date': selected_end_date,
#         'stats': stats
#     }
#     return render(request, 'dashboard.html', context)