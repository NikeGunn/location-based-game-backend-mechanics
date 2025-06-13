from rest_framework import permissions


class IsZoneOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a zone to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the zone
        return obj.owner == request.user


class CanAttackZone(permissions.BasePermission):
    """
    Custom permission to check if user can attack a zone.
    """
    def has_object_permission(self, request, view, obj):
        # User cannot attack their own zone
        if obj.owner == request.user:
            return False

        # User can attack unclaimed zones or zones owned by others
        return True
