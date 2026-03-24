from rest_framework import serializers
from .models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims payload to the token
        token['role'] = user.role
        token['location_id'] = str(user.location_id) if user.location_id else None
        token['community_id'] = str(user.community_id) if user.community_id else None
        token['name'] = user.name
        token['email'] = user.email

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'user_id': str(self.user.id),
            'role': self.user.role,
            'location_id': str(self.user.location_id) if self.user.location_id else None,
            'name': self.user.name,
            'email': self.user.email,
        }
        return data

class UserManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'mobile', 'role', 'community', 'location', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
