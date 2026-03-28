from rest_framework import serializers
from .models import Family
from apps.members.models import Member
from apps.locations.models import Location
from django.db import transaction

class NestedMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'
        read_only_fields = ['id', 'family']

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
        fields = '__all__'
        read_only_fields = ['id', 'family_code', 'created_by']

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
    state_name = serializers.CharField(source='state.name', read_only=True)
    sambhag_name = serializers.CharField(source='sambhag.name', read_only=True)
    loksabha_name = serializers.CharField(source='loksabha.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    vidhansabha_name = serializers.CharField(source='vidhansabha.name', read_only=True)
    ward_name = serializers.CharField(source='ward.name', read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)

    class Meta:
        model = Family
        fields = [
            'id', 'family_code', 'name', 'mobile', 'gotra',
            'state', 'state_name', 
            'sambhag', 'sambhag_name',
            'loksabha', 'loksabha_name',
            'district', 'district_name', 
            'vidhansabha', 'vidhansabha_name',
            'ward', 'ward_name',
            'community', 'community_name',
            'members_count', 'created_at'
        ]

    def get_members_count(self, obj):
        return obj.members.count()

