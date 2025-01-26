from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Department
from .forms import DepartmentForm

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