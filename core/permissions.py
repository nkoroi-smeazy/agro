from rest_framework import permissions

class IsAdminUserOrAgroTech(permissions.BasePermission):
    """
    Allow access only to Admins or Agro-Technicians.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.user_type in ['admin', 'agro']

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Object-level permission: only allow owners of an object (or Admin) to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'admin':
            return True
        # If the object has a 'user' attribute (e.g., Farmer) or a 'farmer' attribute (e.g., Farm, FarmProduce)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'farmer'):
            return obj.farmer.user == request.user
        return False
