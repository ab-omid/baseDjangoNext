from typing import Optional, List, Dict, Any

from app.actions.action import Action


class Handler:
    """
    A base class for handling logic of the application.
    It's the core of the application where authentication, actions, interactions with DB and all other logics happen.
    It provides methods for creating Action objects with predefined error responses.
    """

    @classmethod
    def error(cls, messages: Optional[List[str]] = None) -> Action:
        """
        Create an Action object with a predefined error response.

        Parameters:
        - messages (Optional[List[str]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a predefined error response.
        """
        return Action().something_went_wrong(messages)

    @classmethod
    def unauthorized(cls, messages: Optional[List[str]] = None) -> Action:
        """
        Create an Action object with a predefined unauthorized response.

        Parameters:
        - messages (Optional[List[str]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a predefined unauthorized response.
        """
        return Action().unauthorized(messages)

    @classmethod
    def unprocessable_entity(cls, messages: Optional[List[str]] = None) -> Action:
        """
        Create an Action object with a predefined unprocessable entity response.

        Parameters:
        - messages (Optional[List[str]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a predefined unprocessable entity response.
        """
        return Action().unprocessable_entity(messages)

    @classmethod
    def not_found(cls, messages: Optional[List[str]] = None) -> Action:
        """
        Create an Action object with a predefined not found response.

        Parameters:
        - messages (Optional[List[str]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a predefined not found response.
        """
        return Action().not_found(messages)

    @classmethod
    def bad_request(cls, messages: Optional[List[str]] = None) -> Action:
        """
        Create an Action object with a predefined bad request response.

        Parameters:
        - messages (Optional[List[str]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a predefined bad request response.
        """
        return Action().bad_request(messages)

    @classmethod
    def forbidden(cls, messages: Optional[List[str]] = None) -> Action:
        """
        Create an Action object with a predefined forbidden response.

        Parameters:
        - messages (Optional[List[str]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a predefined forbidden response.
        """
        return Action().forbidden(messages)

    @classmethod
    def action(
        cls,
        output: Any = None,
        error: bool = False,
        http_response_code: int = 200,
        error_messages: Optional[List[str]] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ) -> Action:
        """
        Create an Action object with the provided parameters.

        Parameters:
        - output: The output data for the Action.
        - error (bool): Whether the Action represents an error.
        - http_response_code (int): The HTTP response code for the Action.
        - error_messages (Optional[List[str]]): The error messages for the Action.
        - headers (Optional[Dict]): The headers for the HTTP response.
        - cookies (Optional[Dict]): The cookies for the HTTP response.

        Returns:
        - Action: An Action object with the provided parameters.
        """
        return Action(
            output, error, http_response_code, error_messages, headers, cookies
        )
