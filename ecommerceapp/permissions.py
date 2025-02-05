

from rest_framework.permissions import BasePermission

class IsOwnerOfUniqueUrl(BasePermission):
    """
    Custom permission to check if the logged-in user owns the UniqueURL.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the logged-in user is the owner of the UniqueURL
        return obj.user == request.user