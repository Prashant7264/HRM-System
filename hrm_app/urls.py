from hrm_app import views
from django.urls import path
from hr_management import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('dashboard/',views.dashboard),
    path('department/',views.department),
    path('add/', views.add_department, name='add_department'),
    path('update/<int:dept_id>/', views.update_department, name='update_department'),
    path('delete/<int:dept_id>/', views.delete_department, name='delete_department'),
    path('role/',views.role),
    path('add_role/', views.add_role, name='add_role'),
    path('update_role/<int:role_id>/', views.update_role, name='update_role'),
    path('delete_role/<int:role_id>/', views.delete_role, name='delete_role'),
    path('employee/',views.employee),
    path('add_employee/', views.add_employee, name='add_employee'),
    path('update_employee/<int:employee_id>/', views.update_employee, name='update_employee'),
    path('delete_employee/<int:employee_id>/', views.delete_employee, name='delete_employee'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)