from app.actions.action import Action
from app.handlers.handler import Handler
from app.models.user import User
from app.modules.provider.data_provider import DataProvider


class ImpersonationHandler(Handler):
    @classmethod
    def start_impersonation(cls, admin_user: User, target_user_uuid: str) -> Action:
        """
        Start impersonating a user.
        
        Args:
            admin_user (User): The admin user who is starting impersonation.
            target_user_uuid (str): UUID of the user to impersonate.
            
        Returns:
            Action: Action with success message and impersonated user details or error.
        """
        if not admin_user or admin_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])
            
        # Check if user is admin or staff
        if not (admin_user.is_staff or admin_user.is_superuser):
            return cls.forbidden(["Only admin or staff users can impersonate other users"])
        
        try:
            # Get the user to impersonate
            target_user = DataProvider.user(uuid=target_user_uuid)
            
            if not target_user:
                return cls.not_found(["User not found"])
            
            # Don't allow impersonating yourself
            if target_user.uuid == admin_user.uuid:
                return cls.bad_request(["Cannot impersonate yourself"])
            return cls.action(True)
            
        except Exception as e:
            return cls.bad_request([f"Error starting impersonation: {str(e)}"])

    @classmethod
    def stop_impersonation(cls, admin_user: User) -> Action:
        """
        Stop impersonating a user.
        
        Args:
            admin_user (User): The admin user who is stopping impersonation.
            
        Returns:
            Action: Action with success message or error.
        """
        if not admin_user or admin_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])
            
        # Check if user is admin or staff
        if not (admin_user.is_staff or admin_user.is_superuser):
            return cls.forbidden(["Only admin or staff users can stop impersonation"])
        
        return cls.action(True)

    @classmethod
    def get_impersonation_status(cls, admin_user: User, impersonated_user: User = None) -> Action:
        """
        Get current impersonation status.
        
        Args:
            admin_user (User): The admin user.
            impersonated_user (User, optional): The impersonated user if any.
            
        Returns:
            Action: Action with impersonation status.
        """
        if not admin_user or admin_user.is_anonymous:
            return cls.unauthorized(["User not authenticated"])
            
        # Check if user is admin or staff
        if not (admin_user.is_staff or admin_user.is_superuser):
            return cls.forbidden(["Only admin or staff users can check impersonation status"])
        
        if impersonated_user:
            return cls.action(True)
        else:
            return cls.action(False)
