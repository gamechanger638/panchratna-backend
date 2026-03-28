from rest_framework import serializers
from .models import Member

class MemberSerializer(serializers.ModelSerializer):
    family_name = serializers.ReadOnlyField(source='family.name')
    state_name = serializers.ReadOnlyField(source='family.state.name')
    sambhag_name = serializers.ReadOnlyField(source='family.sambhag.name')
    loksabha_name = serializers.ReadOnlyField(source='family.loksabha.name')
    district_name = serializers.ReadOnlyField(source='family.district.name')
    vidhansabha_name = serializers.ReadOnlyField(source='family.vidhansabha.name')
    ward_name = serializers.ReadOnlyField(source='family.ward.name')
    community_name = serializers.ReadOnlyField(source='family.community.name')
    family_gotra = serializers.ReadOnlyField(source='family.gotra')
    
    class Meta:
        model = Member
        fields = '__all__'
