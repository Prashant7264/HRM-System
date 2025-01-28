from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Department, Role, User
from .forms import DepartmentForm, RoleForm, UserForm

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
    for user in users:
        user.is_active = "Active" if user.is_active else "Inactive"
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
        user.status = False  # Mark as inactive
        user.save()
        messages.warning(request, "Employee marked as inactive.")
        return redirect('/employee')
    return render(request, 'delete_employee.html', {'user': user})
