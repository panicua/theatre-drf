from rest_framework.throttling import SimpleRateThrottle


class StaffRateThrottle(SimpleRateThrottle):
    scope = "staff"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None

        if request.user.is_staff:
            return self.cache_format % {
                "scope": self.scope,
                "ident": request.user.pk,
            }
        return None


class UserRateThrottle(SimpleRateThrottle):
    scope = "user"

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None

        if not request.user.is_staff:
            return self.cache_format % {
                "scope": self.scope,
                "ident": request.user.pk,
            }
        return None
