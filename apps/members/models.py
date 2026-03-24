from django.db import models
import uuid

class Member(models.Model):
    MARITAL_STATUS_CHOICES = (
        ('married', 'Married'),
        ('unmarried', 'Unmarried'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey('families.Family', on_delete=models.CASCADE, related_name='members')
    name = models.CharField(max_length=255)
    relation = models.CharField(max_length=100)
    dob = models.DateField(blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['mobile']),
        ]

    def __str__(self):
        return f"{self.name} ({self.relation})"
