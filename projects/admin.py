from django.contrib import admin
from .models import Project, Worker, Material, MaterialTransaction, Expense, Payment, LabourAttendance, Invoice, UserProfile
admin.site.register([Project, Worker, Material, MaterialTransaction, Expense, Payment, LabourAttendance, Invoice, UserProfile])
