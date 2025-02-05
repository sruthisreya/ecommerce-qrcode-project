from rest_framework.permissions import BasePermission

class IsOwnerOfUniqueUrl(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.unique_url.user == request.user