from rest_framework import permissions

class IsOrgMember(permissions.BasePermission):
    """Allows access only to authenticated users with an organization."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.organization)

class IsOrgAdminOrOwner(permissions.BasePermission):
    """Allows access only to users who are owner or admin of their organization."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ("owner", "admin")
        )
