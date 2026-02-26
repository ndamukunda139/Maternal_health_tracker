from rest_framework import permissions


# Custom permission class for visits to enforce role-based access control
class VisitPermission(permissions.BasePermission):
    """
    Patients: read-only access to their own visits.
    Doctors, nurses, admins: full CRUD access.
    """

    def has_permission(self, request, view):
        # Only allow authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.role == 'patient':
            if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
                # Visits link to patient → patient.user is the actual CustomUser
                return obj.patient.user == user
            return False  # block create, update, delete for patients

        if user.role in ['doctor', 'nurse', 'admin']:
            return True

        return False
