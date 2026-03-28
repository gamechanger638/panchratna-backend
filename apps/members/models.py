from django.db import models
import uuid
from django.utils import timezone

class Member(models.Model):
    MARITAL_STATUS_CHOICES = (
        ('married', 'Married'),
        ('unmarried', 'Unmarried'),
        ('widow', 'Widow'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced'),
    )
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey('families.Family', on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, blank=True, null=True) # Added
    relation = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male')
    dob = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=255, blank=True, null=True) # Added
    blood_group = models.CharField(max_length=10, blank=True, null=True) # Added
    education = models.CharField(max_length=255, blank=True, null=True)
    degree_diploma = models.CharField(max_length=255, blank=True, null=True) # Added
    profession = models.CharField(max_length=255, blank=True, null=True) # Profession Type
    occupation_designation = models.CharField(max_length=255, blank=True, null=True) # Added
    organization_company = models.CharField(max_length=255, blank=True, null=True) # Added
    monthly_income = models.CharField(max_length=100, blank=True, null=True) # Added
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True) # Added
    email = models.EmailField(blank=True, null=True) # Added
    facebook = models.CharField(max_length=255, blank=True, null=True) # Added
    current_address = models.TextField(blank=True, null=True) # Added
    height = models.CharField(max_length=50, blank=True, null=True)
    colour = models.CharField(max_length=50, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    photo1 = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    gotra_image = models.ImageField(upload_to='gotra_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['mobile']),
            models.Index(fields=['gender']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return f"{self.name} ({self.relation})"
