from django.db import models
from django.utils.timezone import now

# Create your models here.
class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.dept_name
    
class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.role_name

class User(models.Model):
    employee_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)  # for use hashed passwords
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    role_id = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    dept_id = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    reporting_manager_id = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates'
    )
    date_of_joining = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low')
    ]
    TYPE_CHOICES = [
        ('Individual', 'Individual'),
        ('Team', 'Team')
    ]

    task_id = models.AutoField(primary_key=True)
    task_title = models.CharField(max_length=100)
    task_description = models.TextField(max_length=300)
    task_priority = models.CharField(max_length=200, choices=PRIORITY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    task_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_title

class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ]

    assignment_id = models.AutoField(primary_key=True)
    task_id = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    employee_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks_assigned')
    assigned_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='Pending')
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.task.task_title} assigned to {self.user.username}"