from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Project(models.Model):
    STATUS_CHOICES = [("Planning","Planning"),("In Progress","In Progress"),("On Hold","On Hold"),("Completed","Completed")]
    name = models.CharField(max_length=160)
    client_name = models.CharField(max_length=120)
    site_address = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    progress = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Planning")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Worker(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=80, default="Worker")
    daily_wage = models.DecimalField(max_digits=9, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="workers")
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class Material(models.Model):
    name = models.CharField(max_length=120)
    unit = models.CharField(max_length=30, default="bag")
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    low_stock_threshold = models.DecimalField(max_digits=12, decimal_places=2, default=5)
    supplier_name = models.CharField(max_length=150, blank=True)
    supplier_phone = models.CharField(max_length=20, blank=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="materials")
    updated_at = models.DateTimeField(auto_now=True)
    @property
    def stock_value(self): return self.quantity * self.unit_cost
    @property
    def is_low_stock(self): return self.quantity <= self.low_stock_threshold
    def __str__(self): return f"{self.name} - {self.project.name}"

class MaterialTransaction(models.Model):
    TYPE_CHOICES = [("Purchase","Purchase"),("Usage","Usage"),("Adjustment","Adjustment")]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supplier_name = models.CharField(max_length=150, blank=True)
    reference = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    notes = models.TextField(blank=True)
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old = None
        if not is_new:
            old = MaterialTransaction.objects.filter(pk=self.pk).first()
        if old:
            self._apply_stock(old, reverse=True)
        super().save(*args, **kwargs)
        self._apply_stock(self, reverse=False)
    @staticmethod
    def _apply_stock(tx, reverse=False):
        qty = tx.quantity
        if tx.transaction_type == "Usage": qty = -qty
        elif tx.transaction_type == "Adjustment": qty = qty
        if reverse: qty = -qty
        Material.objects.filter(pk=tx.material_id).update(quantity=models.F("quantity") + qty)
    def delete(self, *args, **kwargs):
        self._apply_stock(self, reverse=True)
        super().delete(*args, **kwargs)
    def __str__(self): return f"{self.transaction_type}: {self.material.name}"

class Expense(models.Model):
    CATEGORY_CHOICES = [("Labour","Labour"),("Materials","Materials"),("Transport","Transport"),("Equipment","Equipment"),("Other","Other")]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="expenses")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="Other")
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()
    def __str__(self): return f"{self.description} (₹{self.amount})"

class Payment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="payments")
    payer_name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    date = models.DateField()
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    def __str__(self): return f"{self.payer_name} - ₹{self.amount}"

class LabourAttendance(models.Model):
    STATUS_CHOICES = [("Present","Present"),("Absent","Absent"),("Half Day","Half Day"),("Leave","Leave")]
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name="attendance_records")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="Present")
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    overtime_rate = models.DecimalField(max_digits=9, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    notes = models.CharField(max_length=200, blank=True)
    class Meta:
        unique_together = ("worker", "project", "date")
        ordering = ["-date", "worker__name"]
    @property
    def wage_amount(self):
        base = self.worker.daily_wage
        if self.status == "Absent" or self.status == "Leave": base = Decimal("0")
        elif self.status == "Half Day": base = base / Decimal("2")
        return base + self.overtime_hours * self.overtime_rate
    def __str__(self): return f"{self.worker} - {self.date}"

class Invoice(models.Model):
    STATUS_CHOICES = [("Draft","Draft"),("Sent","Sent"),("Partially Paid","Partially Paid"),("Paid","Paid"),("Overdue","Overdue")]
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="invoices")
    invoice_number = models.CharField(max_length=40, unique=True)
    client_name = models.CharField(max_length=150)
    client_address = models.TextField(blank=True)
    client_gstin = models.CharField(max_length=20, blank=True)
    description = models.CharField(max_length=255)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18, validators=[MinValueValidator(0), MaxValueValidator(100)])
    advance_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    issue_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Draft")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def gst_amount(self): return (self.subtotal * self.gst_rate / Decimal("100")).quantize(Decimal("0.01"))
    @property
    def total_amount(self): return self.subtotal + self.gst_amount
    @property
    def balance_due(self): return max(Decimal("0"), self.total_amount - self.advance_paid - self.amount_paid)
    def __str__(self): return self.invoice_number

class UserProfile(models.Model):
    ROLE_CHOICES = [("Admin","Admin"),("Accountant","Accountant"),("Site Manager","Site Manager")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="Site Manager")
    projects = models.ManyToManyField(Project, blank=True, related_name="assigned_users")
    def __str__(self): return f"{self.user.username} ({self.role})"
