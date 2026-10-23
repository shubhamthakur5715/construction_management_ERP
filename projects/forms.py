from django import forms
from .models import Project, Worker, Material, MaterialTransaction, Expense, Payment, LabourAttendance, Invoice, UserProfile

class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

class ProjectForm(StyledModelForm):
    class Meta:
        model = Project
        fields = ["name","client_name","site_address","budget","start_date","end_date","progress","status","notes"]
        widgets = {"start_date": forms.DateInput(attrs={"type":"date"}), "end_date": forms.DateInput(attrs={"type":"date"}), "notes": forms.Textarea(attrs={"rows":3})}
class WorkerForm(StyledModelForm):
    class Meta:
        model = Worker
        fields = ["name","phone","role","daily_wage","project","active"]
class MaterialForm(StyledModelForm):
    class Meta:
        model = Material
        fields = ["name","unit","quantity","unit_cost","low_stock_threshold","supplier_name","supplier_phone","project"]
class MaterialTransactionForm(StyledModelForm):
    class Meta:
        model = MaterialTransaction
        fields = ["material","transaction_type","quantity","unit_cost","supplier_name","reference","date","notes"]
        widgets = {"date": forms.DateInput(attrs={"type":"date"}), "notes": forms.Textarea(attrs={"rows":2})}
class ExpenseForm(StyledModelForm):
    class Meta:
        model = Expense
        fields = ["project","category","description","amount","date"]
        widgets = {"date": forms.DateInput(attrs={"type":"date"})}
class PaymentForm(StyledModelForm):
    class Meta:
        model = Payment
        fields = ["project","payer_name","amount","date","reference","notes"]
        widgets = {"date": forms.DateInput(attrs={"type":"date"}), "notes": forms.Textarea(attrs={"rows":2})}
class LabourAttendanceForm(StyledModelForm):
    class Meta:
        model = LabourAttendance
        fields = ["worker","project","date","status","overtime_hours","overtime_rate","notes"]
        widgets = {"date": forms.DateInput(attrs={"type":"date"})}
class InvoiceForm(StyledModelForm):
    class Meta:
        model = Invoice
        fields = ["project","invoice_number","client_name","client_address","client_gstin","description","subtotal","gst_rate","advance_paid","amount_paid","issue_date","due_date","status","notes"]
        widgets = {"client_address": forms.Textarea(attrs={"rows":2}), "issue_date": forms.DateInput(attrs={"type":"date"}), "due_date": forms.DateInput(attrs={"type":"date"}), "notes": forms.Textarea(attrs={"rows":2})}
class UserProfileForm(StyledModelForm):
    class Meta:
        model = UserProfile
        fields = ["role","projects"]
        widgets = {"projects": forms.CheckboxSelectMultiple()}
