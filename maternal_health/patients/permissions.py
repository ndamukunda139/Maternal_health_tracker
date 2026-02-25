from rest_framework import permissions

class PatientProfilePermission(permissions.BasePermission):
    """
    Patients: read-only access to their own profile.
    Doctors, nurses, admins: full CRUD access.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == 'patient':
            if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
                return obj.user == user
            return False  # block create, update, delete

        if user.role in ['doctor', 'nurse', 'admin']:
            return True

        return False


class IsClinicianOrAdmin(permissions.BasePermission):
    """Allow access only to users with role 'doctor', 'nurse' or 'admin'."""

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and getattr(user, 'is_authenticated', False)
            and getattr(user, 'role', None) in ['doctor', 'nurse', 'admin']
        )