from rest_framework import serializers
from .models import MarriageProfile

class MarriageProfileSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = MarriageProfile
        fields = ['id', 'member', 'member_name', 'age', 'height', 'education', 'profession', 'city', 'bio', 'is_active', 'created_at']

    def get_age(self, obj):
        import datetime
        if obj.member.dob:
            today = datetime.date.today()
            return today.year - obj.member.dob.year - ((today.month, today.day) < (obj.member.dob.month, obj.member.dob.day))
        return None

    def validate_member(self, value):
        if value.marital_status != 'unmarried':
            raise serializers.ValidationError("Only unmarried members can create a profile.")
        return value
