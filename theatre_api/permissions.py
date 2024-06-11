from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    """Staff can do anything, all others can only read."""

    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsStaffToDelete(BasePermission):
    """Staff can delete permission."""

    def has_permission(self, request, view):
        if view.action == "destroy":
            return request.user.is_staff
        return True


class IsStaffToCreateDestroyPatchPut(BasePermission):
    """Staff can delete permission."""

    def has_permission(self, request, view):
        if view.action in ("create", "destroy", "patch", "put"):
            return request.user.is_staff
        return True
