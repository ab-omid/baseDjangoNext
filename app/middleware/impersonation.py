from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser
import uuid

User = get_user_model()


class ImpersonationMiddleware(MiddlewareMixin):
    """
    Middleware to handle user impersonation.
    
    This middleware sets request.impersonated_user if a valid impersonation
    session exists. The permission checks for starting/stopping impersonation
    are handled in the controllers/handlers.
    """
    
    def process_request(self, request):
        """
        Process the request and set up impersonation if applicable.
        """
        # Initialize impersonated_user as None
        request.impersonated_user = None
        
        # Get impersonated user UUID from session
        impersonated_user_uuid = request.session.get('impersonated_user_uuid')
        
        if impersonated_user_uuid:
            try:
                # Validate UUID format
                uuid.UUID(impersonated_user_uuid)
                
                # Get the impersonated user
                impersonated_user = User.objects.get(
                    uuid=impersonated_user_uuid
                )
                
                # Only set impersonated user if the user is active
                if impersonated_user.is_active:
                    request.impersonated_user = impersonated_user
                else:
                    # User is inactive, clear the session
                    request.session.pop('impersonated_user_uuid', None)
                
            except (ValueError, User.DoesNotExist):
                # Invalid UUID or user doesn't exist, clear the session
                request.session.pop('impersonated_user_uuid', None)
                
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process the view and ensure impersonated_user is set if needed.
        This runs after authentication middleware but before the view.
        """
        # If impersonated_user is not set but we have a session, try to set it
        if not hasattr(request, 'impersonated_user') or request.impersonated_user is None:
            impersonated_user_uuid = request.session.get('impersonated_user_uuid')
            
            if impersonated_user_uuid:
                try:
                    # Validate UUID format
                    uuid.UUID(impersonated_user_uuid)
                    
                    # Get the impersonated user
                    impersonated_user = User.objects.get(
                        uuid=impersonated_user_uuid
                    )
                    
                    # Only set impersonated user if the user is active
                    if impersonated_user.is_active:
                        request.impersonated_user = impersonated_user
                    else:
                        # User is inactive, clear the session
                        request.session.pop('impersonated_user_uuid', None)
                        
                except (ValueError, User.DoesNotExist):
                    # Invalid UUID or user doesn't exist, clear the session
                    request.session.pop('impersonated_user_uuid', None)
        
        return None
