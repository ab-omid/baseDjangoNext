import json
import random
import string
from typing import List


class StringUtil:
    @staticmethod
    def random_string(size: int = 12, chars=string.digits + string.ascii_letters) -> str:
        """
        Generate a random string of specified size using the given characters.

        Parameters:
        size (int): The length of the random string. Default is 12.
        chars (str): The characters to choose from for generating the random string. Default is digits and lowercase and uppercase letters.

        Returns:
        str: The generated random string.
        """
        return "".join(random.choice(chars) for _ in range(size))

    @staticmethod
    def parse_json_garbage(s: str) -> dict:
        """
        Parse a JSON string that may contain leading garbage characters.

        Parameters:
        s (str): The JSON string to parse.

        Returns:
        dict: The parsed JSON object. If parsing fails, it returns the parsed JSON object up to the error position.
        """
        s = s[next(idx for idx, c in enumerate(s) if c in "{[") :]
        try:
            return json.loads(s)
        except json.JSONDecodeError as e:
            return json.loads(s[: e.pos])

    @staticmethod
    def extract_last_part_of_url(url: str) -> str | None:
        """
        Extract the last part of a URL.

        Parameters:
        url (str): The URL to extract the last part from.

        Returns:
        str | None: The last part of the URL if it is a non-empty string, otherwise None.
        """
        # Check if the URL is a non-empty string
        if not isinstance(url, str) or not url:
            return None

        # Remove the trailing slash if it exists
        if url.endswith("/"):
            url = url[:-1]

        # Split the URL by slashes and return the last part
        return url.rsplit("/", 1)[-1]

    @staticmethod
    def clean_text(input_text: str | None) -> str | None:
        """
        Clean a text by removing special characters, leading/trailing whitespaces, and multiple spaces.

        Parameters:
        input_text (str | None): The text to clean.

        Returns:
        str | None: The cleaned text if the input is not None, otherwise None.
        """
        if input_text is None:
            return None
        # Replace "\_" with an empty string
        cleaned_text = input_text.replace("\\_", "").replace("\\", "").replace("\n", "")

        # Remove leading and trailing whitespaces
        cleaned_text = cleaned_text.strip()

        # Replace multiple spaces with a single space
        cleaned_text = " ".join(cleaned_text.split())

        return cleaned_text

    @staticmethod
    def to_json(obj, class_key=None):
        """
        Convert an object to a JSON-serializable format.

        Parameters:
        obj: The object to convert.
        class_key (str): The key to include in the JSON object for the class name if the object has a __class__ attribute.

        Returns:
        dict: The JSON-serializable object.
        """
        if isinstance(obj, dict):
            data = {}
            if hasattr(obj, "__dict__"):
                for k in obj.__dict__.keys():
                    data[k] = StringUtil.to_json(getattr(obj, k), class_key)
                return data
            return obj
        elif hasattr(obj, "_ast"):
            return StringUtil.to_json(obj._ast())
        elif hasattr(obj, "__iter__") and not isinstance(obj, str):
            return [StringUtil.to_json(v, class_key) for v in obj]
        elif hasattr(obj, "__dict__"):
            data = dict(
                [
                    (key, StringUtil.to_json(value, class_key))
                    for key, value in obj.__dict__.items()
                    if not callable(value) and not key.startswith("_")
                ]
            )
            if class_key is not None and hasattr(obj, "__class__"):
                data[class_key] = obj.__class__.__name__
            return data
        else:
            return obj

    @staticmethod
    def json_to_text(profile: dict | List[dict]) -> str:
        """
        Convert a JSON object or a list of JSON objects to a formatted text.

        Parameters:
        profile (dict | List[dict]): The JSON object or a list of JSON objects to convert.

        Returns:
        str: The formatted text representation of the JSON object(s).
        """
        if isinstance(profile, list):
            return "\n\n".join(StringUtil.json_to_text(p) for p in profile)
        return "".join(f"{key}: {value}\t\n" for key, value in profile.items())
