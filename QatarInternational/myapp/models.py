from django.db import models

# Create your models here.

class Users(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    role = models.CharField(max_length=50)       # Simple string field
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
