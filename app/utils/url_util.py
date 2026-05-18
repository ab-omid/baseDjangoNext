from urllib.parse import urljoin

from requests.models import PreparedRequest

from app.utils.string_util import StringUtil


class UrlUtil:
    @staticmethod
    def get_route(
        path: str = None, query_params: dict = None, base_url: str = None
    ) -> str:
        """
        Generate a complete URL by combining the base URL, path, and query parameters.

        Parameters:
        path (str): The path to be appended to the base URL. Default is None.
        query_params (dict): The query parameters to be added to the URL. Default is None.
        base_url (str): The base URL to be used. If not provided, the BASE_URL from the AppConfig will be used.

        Returns:
        str: The complete URL with the provided path, query parameters, and base URL.
        """
        from app.config.app import AppConfig

        url = AppConfig.BASE_URL if base_url is None else base_url
        if path is not None:
            url = urljoin(url, path)
        if query_params is not None:
            req = PreparedRequest()
            req.prepare_url(url, query_params)
            url = req.url
        return url

    @staticmethod
    def is_linkedin_profile_url(url: str):
        """
        Check if the URL is a LinkedIn profile URL.

        Parameters:
        url (str): The URL to check.

        Returns:
        bool: True if the URL is a LinkedIn profile URL, False otherwise.
        """
        return url.startswith("https://www.linkedin.com/in/") or url.startswith(
            "https://linkedin.com/in/"
        )