from typing import Dict


class BaseApiModel:
    class RESPONSE_FIELDS:
        type = "type"
        key = "key"
        created_at = "created_at"
        next_page_token = "next_page_token"
        previous_page_token = "previous_page_token"
        items = "items"
        total_results = "total_results"

    def api_response(self, other_properties: dict | None = None, **kwargs) -> dict:
        """
        This method generates a base API response with the type of the current model.

        Parameters:
        **kwargs: Arbitrary keyword arguments. These are not used in this method, but can be used in subclasses.

        Returns:
        dict: A dictionary containing the type of the current model.
        """
        return {
            self.RESPONSE_FIELDS.type: self.__class__.__name__,
            **(other_properties or {}),
        }

    @classmethod
    def api_response_schema(
        cls, other_properties: dict | None = None, **kwargs
    ) -> Dict:
        """
        This method generates a base API response schema for the current model.

        Parameters:
        **kwargs: Arbitrary keyword arguments. These are not used in this method, but can be used in subclasses.

        Returns:
        Dict: A dictionary representing the API response schema. The schema includes a property for the type of the current model.
        """
        return {
            "type": "object",
            "properties": {
                **(other_properties or {}),
                cls.RESPONSE_FIELDS.type: {
                    "type": "string",
                    "title": "Item Type",
                    "description": "Item Type",
                    "readonly": True,
                    "required": True,
                    "nullable": False,
                    "example": cls.__class__.__name__,
                }
            },
            "required": [cls.RESPONSE_FIELDS.type],
        }
