from django.db import models

# Create your models here.

class Users(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    student_id = models.CharField(max_length=50, unique=True, default='0')
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Notice(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    url = models.URLField(blank=True, null=True, help_text="Optional Google Drive link")
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=100, default="General")

    def __str__(self):
        return self.title


class Student(models.Model):
    s_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    s_name = models.CharField(max_length=150)
    s_roll = models.CharField(max_length=100)
    s_class = models.CharField(max_length=50, blank=True, null=True)
    
    present_address = models.CharField(max_length=255, blank=True, null=True)
    permanent_address = models.CharField(max_length=255, blank=True, null=True)
    
    father_name = models.CharField(max_length=150, blank=True, null=True)
    father_number = models.CharField(max_length=20, blank=True, null=True)
    
    mother_name = models.CharField(max_length=150, blank=True, null=True)
    mother_number = models.CharField(max_length=20, blank=True, null=True)

    password = models.CharField(max_length=128, blank=True, null=True)
    pp_url = models.URLField(blank=True, null=True, help_text="Optional profile picture link")

    def __str__(self):
        return f"{self.s_name} ({self.s_roll})"


# ✅ New Table for Payment History
class PaymentHistory(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)  # FK to Users table
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    via = models.CharField(max_length=50, choices=[('bkash', 'bKash'), ('on_hand', 'On Hand')])

    def __str__(self):
        return f"{self.user.username} - {self.amount} via {self.via}"
