from django.urls import path

from .views import expense_list, expense_entry_create,expense_delete,expense_edit,expense_report
from expenses.check_superuser import check_superuser
from expenses.driver_assignment_list import driver_assignment_list, driver_assignment_edit, driver_assignment_delete
from expenses.list import driver_list, vehicle_list
from expenses.expense_export_excel import expense_export_excel



urlpatterns = [
    
    path('', expense_list, name='expense_list'),
    path('new/', expense_entry_create, name='expense_create'),
    path('delete/<int:pk>/', expense_delete, name='expense_delete'),
    path('edit/<int:pk>/',expense_edit, name='expense_edit'),
    path("expenses/report/", expense_report, name="expense_report"),
    path("check-superuser/", check_superuser, name="check_superuser"),
    path('assignments/', driver_assignment_list, name='driver_assignment_list'),
     path('driver_assignments/edit/<int:pk>/', driver_assignment_edit, name='driver_assignment_edit'),
    path('driver_assignments/delete/<int:pk>/', driver_assignment_delete, name='driver_assignment_delete'),
    path('drivers/', driver_list, name='driver_list'),
    path('vehicles/', vehicle_list, name='vehicle_list'),
    path('expenses/export_excel/',expense_export_excel, name='expense_export_excel'),

   

]
