from django.urls import path
from . import views
urlpatterns = [
 path("", views.dashboard, name="dashboard"),
 path("projects/", views.project_list, name="project_list"),
 path("projects/add/", views.project_create, name="project_create"),
 path("projects/<int:pk>/edit/", views.project_edit, name="project_edit"),
 path("projects/<int:pk>/delete/", views.project_delete, name="project_delete"),
 path("workers/", views.worker_list, name="worker_list"), path("workers/add/", views.worker_create, name="worker_create"),
 path("materials/", views.material_list, name="material_list"), path("materials/add/", views.material_create, name="material_create"),
 path("materials/transaction/add/", views.material_transaction_create, name="material_transaction_create"),
 path("expenses/", views.expense_list, name="expense_list"), path("expenses/add/", views.expense_create, name="expense_create"),
 path("payments/", views.payment_list, name="payment_list"), path("payments/add/", views.payment_create, name="payment_create"),
 path("attendance/", views.attendance_list, name="attendance_list"), path("attendance/add/", views.attendance_create, name="attendance_create"),
 path("invoices/", views.invoice_list, name="invoice_list"), path("invoices/add/", views.invoice_create, name="invoice_create"),
 path("invoices/<int:pk>/", views.invoice_detail, name="invoice_detail"),
 path("reports/profit-loss/", views.profit_loss, name="profit_loss"),
 path("reports/export/<str:kind>/", views.export_report, name="export_report"),
 path("settings/users/", views.user_roles, name="user_roles"),
 path("settings/users/<int:pk>/", views.user_role_edit, name="user_role_edit"),
]
