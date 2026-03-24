from django.db import models
import uuid

class Location(models.Model):
    LOCATION_TYPES = (
        ('state', 'State'),
        ('sambhag', 'Sambhag'),
        ('loksabha', 'Loksabha'),
        ('district', 'District'),
        ('zone', 'Zone'),
        ('vidhansabha', 'Vidhansabha'),
        ('ward', 'Ward'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=LOCATION_TYPES)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    community = models.ForeignKey('community.Community', on_delete=models.CASCADE, null=True, blank=True, related_name='locations')

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
