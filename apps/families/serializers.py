from rest_framework import serializers
from .models import Family
from apps.members.models import Member
from apps.locations.models import Location
from django.db import transaction

class NestedMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'name', 'relation', 'dob', 'education', 'profession', 'marital_status', 'mobile']
        read_only_fields = ['id']

class FamilySerializer(serializers.ModelSerializer):
    members = NestedMemberSerializer(many=True, required=False)
    members_count = serializers.SerializerMethodField()
    state = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(type='state'), allow_null=True, required=False)
    sambhag = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(type='sambhag'), allow_null=True, required=False)
    loksabha = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(type='loksabha'), allow_null=True, required=False)
    district = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(type='district'), allow_null=True, required=False)
    vidhansabha = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(type='vidhansabha'), allow_null=True, required=False)
    ward = serializers.PrimaryKeyRelatedField(queryset=Location.objects.filter(type='ward'), allow_null=True, required=False)

    class Meta:
        model = Family
        fields = [
            'id', 'family_code', 'name', 'father_or_husband_name', 'mother_name',
            'gotra', 'dob', 'age', 'education', 'profession', 'mobile', 'email',
            'social_role', 'state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward',
            'permanent_address', 'current_address', 'members', 'members_count', 'community'
        ]
        read_only_fields = ['id', 'family_code']

    def get_members_count(self, obj):
        return obj.members.count()

    def validate(self, data):
        ward = data.get('ward')
        vidhansabha = data.get('vidhansabha')
        district = data.get('district')
        loksabha = data.get('loksabha')
        sambhag = data.get('sambhag')
        state = data.get('state')

        if ward and vidhansabha and ward.parent != vidhansabha:
            raise serializers.ValidationError({"ward": "Ward must belong to the selected Vidhansabha."})
        if vidhansabha and district and vidhansabha.parent != district:
            raise serializers.ValidationError({"vidhansabha": "Vidhansabha must belong to the selected District."})
        if district and loksabha and district.parent != loksabha:
            raise serializers.ValidationError({"district": "District must belong to the selected Loksabha."})
        if loksabha and sambhag and loksabha.parent != sambhag:
            raise serializers.ValidationError({"loksabha": "Loksabha must belong to the selected Sambhag."})
        if sambhag and state and sambhag.parent != state:
            raise serializers.ValidationError({"sambhag": "Sambhag must belong to the selected State."})
            
        return data

    @transaction.atomic
    def create(self, validated_data):
        members_data = validated_data.pop('members', [])
        validated_data['created_by'] = self.context['request'].user
        family = Family.objects.create(**validated_data)
        
        for member_data in members_data:
            Member.objects.create(family=family, **member_data)
            
        return family

    @transaction.atomic
    def update(self, instance, validated_data):
        members_data = validated_data.pop('members', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if members_data is not None:
            instance.members.all().delete()
            for member_data in members_data:
                Member.objects.create(family=instance, **member_data)
                
        return instance

class FamilyListSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    state = serializers.StringRelatedField()
    sambhag = serializers.StringRelatedField()
    loksabha = serializers.StringRelatedField()
    district = serializers.StringRelatedField()
    vidhansabha = serializers.StringRelatedField()
    ward = serializers.StringRelatedField()
    community = serializers.StringRelatedField()

    class Meta:
        model = Family
        fields = ['id', 'family_code', 'name', 'mobile', 'state', 'sambhag', 'loksabha', 'district', 'vidhansabha', 'ward', 'members_count', 'community']

    def get_members_count(self, obj):
        return obj.members.count()

