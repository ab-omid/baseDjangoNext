from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from app.models.base_model import BaseModel as BaseDjangoModel

from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
import csv


class Action:
    """
    A class used to represent an action in the application.
    It encapsulates the output, error status, HTTP response code, error messages, headers, and cookies of the action.
    """
    output: Any
    error: bool
    http_response_code: int
    error_messages: List
    headers: Dict | None
    cookies: Dict | None

    def __init__(
        self,
        output: Any = None,
        error: bool = False,
        http_response_code: int = 200,
        error_messages: Optional[List[str]] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
    ):
        if error_messages is None:
            error_messages = []

        self.output = output
        self.error = error
        self.http_response_code = http_response_code
        self.error_messages = error_messages
        self.headers = headers
        self.cookies = cookies

    def success(self) -> bool:
        """
        Check if this action is successful.

        Returns:
        - bool: True if the action is successful, False otherwise.
        """
        return not self.error

    def to_dict(self) -> Dict:
        """
        Convert the action object to a dictionary.

        Returns:
        - Dict: A dictionary representation of the action object.
        """
        output = self.output
        if output is not None and isinstance(output, BaseDjangoModel):
            from django.core import serializers

            output = serializers.serialize("json", [output])
        if output is not None and isinstance(output, BaseModel):
            output = output.model_dump()

        return {
            "output": output,
            "error": self.error,
            "http_response_code": self.http_response_code,
            "error_messages": self.error_messages,
        }

    def __str__(self) -> str:
        """
        Convert the action object to a JSON string.

        Returns:
        - str: A JSON string representation of the action object.
        """
        return json.dumps(self.to_dict())

    def json_response(self) -> JsonResponse:
        """
        Create a JSON response from the action object.

        Returns:
        - JsonResponse: A JSON response object containing the action data.
        """
        headers = self.headers if self.headers is not None else {}
        response = JsonResponse(self.to_dict(), status=self.http_response_code, headers=headers)
        if self.cookies is not None:
            for key in self.cookies.keys():
                response.set_cookie(key, self.cookies[key])
        return response

    def redirect_response(self, url: str) -> HttpResponseRedirect:
        """
        Create a redirect response to the specified URL.

        Parameters:
        - url (str): The URL to redirect to.

        Returns:
        - HttpResponseRedirect: A redirect response object to the specified URL.
        """
        return HttpResponseRedirect(url, status=self.http_response_code, headers=self.headers)

    def csv_response(
        self,
        fieldnames: list[str],
        filename: str = "export.csv",
    ) -> HttpResponse:
        """
        Create a CSV response from the action output.
        
        The output should be a dict with 'items' key containing a list of dicts,
        or a list of dicts directly.
        
        Parameters:
        - fieldnames: List of column names for CSV header
        - filename: Name of the downloaded file
        
        Returns:
        - HttpResponse: A CSV response object
        """
        if self.error:
            # Return error as JSON if CSV export fails
            return self.json_response()
        
        # Extract items from output
        output = self.output
        if isinstance(output, dict):
            items = output.get('items', [])
        elif isinstance(output, list):
            items = output
        else:
            items = []
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.DictWriter(
            response,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        
        for row in items:
            # Extract values from row dict
            writer.writerow({k: row.get(k, "") for k in fieldnames})
        
        return response

    def something_went_wrong(self, error_messages: Optional[List[Any]] = None) -> Action:
        """
        Set the action as an error with the specified error messages.

        Parameters:
        - error_messages (Optional[List[Any]]): The error messages to be set.

        Returns:
        - Action: The updated action object.
        """
        if error_messages is None:
            error_messages = ["Something went wrong."]
        self.error = True
        self.http_response_code = 500
        self.error_messages = error_messages
        return self

    def unauthorized(self, error_messages: Optional[List[Any]] = None) -> Action:
        """
        Set the action as an unauthorized error with the specified error messages.

        Parameters:
        - error_messages (Optional[List[Any]]): The error messages to be set.

        Returns:
        - Action: The updated action object.
        """
        if error_messages is None:
            error_messages = ["Unauthorized Action."]
        self.error = True
        self.http_response_code = 401
        self.error_messages = error_messages
        return self

    def not_found(self, error_messages: Optional[List[Any]] = None) -> Action:
        """
        Create a not found action.

        Parameters:
        - error_messages (Optional[List[Any]]): The error messages to include in the response.

        Returns:
        - Action: A not found action.
        """
        if error_messages is None:
            error_messages = []
        return Action(
            output=None,
            error=True,
            http_response_code=404,
            error_messages=error_messages,
        )

    def bad_request(self, error_messages: Optional[List[Any]] = None) -> Action:
        """
        Create a bad request action.

        Parameters:
        - error_messages (Optional[List[Any]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a bad request response.
        """
        if error_messages is None:
            error_messages = []
        return Action(
            error=True,
            http_response_code=400,
            error_messages=error_messages,
        )

    def forbidden(self, error_messages: Optional[List[Any]] = None) -> Action:
        """
        Create a forbidden action.

        Parameters:
        - error_messages (Optional[List[Any]]): The error messages to include in the response.

        Returns:
        - Action: An Action object with a forbidden response.
        """
        if error_messages is None:
            error_messages = []
        return Action(
            error=True,
            http_response_code=403,
            error_messages=error_messages,
        )

    def unprocessable_entity(self, error_messages: Optional[List[str]] = None) -> Action:
        """
        Set the action as an unprocessable entity error with the specified error messages.

        Parameters:
        - error_messages (Optional[List[str]]): The error messages to be set.

        Returns:
        - Action: The updated action object.
        """
        if error_messages is None:
            error_messages = ["Unprocessable Entity"]
        self.error = True
        self.http_response_code = 422
        self.error_messages = error_messages
        return self
    def throttled(self, retry_after: int | None = None) -> Action:
        """
        Set the action as a throttled error with the specified retry after value.

        Parameters:
        - retry_after (int | None): The number of seconds to wait before retrying the request.

        Returns:
        - Action: The updated action object.
        """
        if retry_after is None:
            error_messages = ["Request was throttled"]
        else:
            error_messages = [f"Request was throttled retry after {retry_after} seconds."]
        self.error = True
        self.http_response_code = 429
        self.error_messages = error_messages
        return self

    @classmethod
    def generate_schema(cls, output_structure: Dict, is_single_output: bool = False) -> Dict:
        """
        Generate a JSON schema for the action output based on the output structure and whether it is a single output.

        Parameters:
        - output_structure (Dict): The structure of the output.
        - is_single_output (bool): Whether the output is a single object or a list of objects.

        Returns:
        - Dict: The generated JSON schema.
        """
        if is_single_output:
            return {
                "type": "object",
                "properties": {
                    "output": output_structure,
                    "error": {"type": "boolean"},
                    "http_response_code": {"type": "integer"},
                    "error_messages": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["output", "error", "http_response_code", "error_messages"],
            }

        return {
            "type": "object",
            "properties": {
                "output": {
                    "type": "object",
                    "properties": {"items": {"type": "array", "items": output_structure}},
                },
                "error": {"type": "boolean"},
                "http_response_code": {"type": "integer"},
                "error_messages": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["output", "error", "http_response_code", "error_messages"],
        }

    @classmethod
    def prepare_api_output(
        cls,
        values: list | None = None,
        next_page_token: str | None = None,
        previous_page_token: str | None = None,
        total_results: int | None = None,
        **kwargs,
    ):
        """
        Prepare the API output for a list of values with optional next and previous page tokens.

        Parameters:
        - values (list | None): The list of values to prepare the output for.
        - next_page_token (str | None): The next page token.
        - previous_page_token (str | None): The previous page token.
        - total_results (int | None): The total number of results.
        - kwargs: Additional keyword arguments to pass to the BaseApiModel.api_response method.

        Returns:
        - Dict: The prepared API output.
        """
        from app.models.base_api_model import BaseApiModel

        values = values if values is not None else []
        output = []
        for value in values:
            if isinstance(value, BaseApiModel):
                output.append(value.api_response(**kwargs))
            else:
                output.append(value)
        return {
            BaseApiModel.RESPONSE_FIELDS.items: output,
            BaseApiModel.RESPONSE_FIELDS.next_page_token: next_page_token,
            BaseApiModel.RESPONSE_FIELDS.previous_page_token: previous_page_token,
            BaseApiModel.RESPONSE_FIELDS.total_results: total_results,
        }

    @classmethod
    def prepare_api_single_output(cls, value=None, **kwargs):
        """
        Prepare the API output for a single value.

        Parameters:
        - value: The value to prepare the output for.
        - kwargs: Additional keyword arguments to pass to the BaseApiModel.api_response method.

        Returns:
        - Any: The prepared API output for the single value.
        """
        from app.models.base_api_model import BaseApiModel

        return value.api_response(**kwargs) if isinstance(value, BaseApiModel) else value