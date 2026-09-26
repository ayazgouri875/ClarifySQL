from rest_framework import permissions

class IsOrganizationMember(permissions.BasePermission):
    """Allows access only to members of the organization."""
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.organization_id == obj.id)

class IsOrganizationAdmin(permissions.BasePermission):
    """Allows access only to owners and admins of the organization."""
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.organization_id == obj.id and
            request.user.role in ("owner", "admin")
        )
