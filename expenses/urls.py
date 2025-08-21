from django.urls import path

from .views import expense_list, expense_entry_create,expense_delete,expense_edit,expense_report
from expenses.check_superuser import check_superuser

urlpatterns = [
    
    path('', expense_list, name='expense_list'),
    path('new/', expense_entry_create, name='expense_create'),
    path('delete/<int:pk>/', expense_delete, name='expense_delete'),
    path('edit/<int:pk>/',expense_edit, name='expense_edit'),
    path("expenses/report/", expense_report, name="expense_report"),
    path("check-superuser/", check_superuser, name="check_superuser"),

]
