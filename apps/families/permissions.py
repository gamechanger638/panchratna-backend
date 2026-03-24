from rest_framework import permissions

class RoleBasedFamilyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'super_admin':
            return True
        if user.role == 'state_admin' and obj.state == user.location:
            return True
        if user.role == 'district_admin' and obj.district == user.location:
            return True
        if user.role == 'zone_admin': # Zone logic might be custom depending on parent
            pass 
        if user.role == 'vidhansabha_admin' and obj.vidhansabha == user.location:
            return True
        if user.role == 'ward_volunteer' and obj.ward == user.location:
            return True
        return False
