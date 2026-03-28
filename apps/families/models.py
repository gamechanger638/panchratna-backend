from django.db import models
from django.conf import settings
import uuid

class Family(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    community = models.ForeignKey('community.Community', on_delete=models.CASCADE, null=True, blank=True, related_name='families')
    family_code = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=255)
    father_or_husband_name = models.CharField(max_length=255, blank=True, null=True)
    mother_name = models.CharField(max_length=255, blank=True, null=True)
    gotra = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    social_role = models.CharField(max_length=255, blank=True, null=True)
    
    state = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, related_name='family_states')
    sambhag = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, related_name='family_sambhags')
    loksabha = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, related_name='family_loksabhas')
    district = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, related_name='family_districts')
    vidhansabha = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, related_name='family_vidhansabhas')
    ward = models.ForeignKey('locations.Location', on_delete=models.SET_NULL, null=True, related_name='family_wards')
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    permanent_address = models.TextField(blank=True, null=True)
    current_address = models.TextField(blank=True, null=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_families')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Families"
        indexes = [
            models.Index(fields=['mobile']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.family_code})"

    def save(self, *args, **kwargs):
        if not self.family_code:
            last = Family.objects.order_by('-created_at').first()
            if last and last.family_code.startswith('F'):
                try:
                    num = int(last.family_code[1:]) + 1
                    self.family_code = f"F{num:04d}"
                except ValueError:
                    self.family_code = "F0001"
            else:
                self.family_code = "F0001"
        super().save(*args, **kwargs)
