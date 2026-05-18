import re
from datetime import datetime, date
from typing import Optional, Tuple


class DateUtil:
    """Utility class for parsing date ranges from various formats."""

    @staticmethod
    def parse_single_date(date_string: str) -> Optional[date]:
        """
        Parse a single date string and return a date object.

        Supports formats like:
        - "4/1/2021"
        - "04/01/2021"
        - "2021-04-01"
        - "April 1, 2021"

        Args:
            date_string: The date string to parse

        Returns:
            Date object or None if parsing fails
        """
        if not date_string or not isinstance(date_string, str):
            return None

        date_string = date_string.strip()

        # Try different patterns
        patterns = [
            # MM/DD/YYYY or M/D/YYYY
            r"(\d{1,2})/(\d{1,2})/(\d{4})",
            # YYYY-MM-DD
            r"(\d{4})-(\d{1,2})-(\d{1,2})",
            # Month DD, YYYY or Month D, YYYY
            r"([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})",
        ]

        for pattern in patterns:
            match = re.search(pattern, date_string, re.IGNORECASE)
            if match:
                groups = match.groups()

                if len(groups) == 3 and "/" in pattern:
                    # MM/DD/YYYY format
                    month, day, year = groups
                    try:
                        return date(int(year), int(month), int(day))
                    except ValueError:
                        continue

                elif len(groups) == 3 and "-" in pattern:
                    # YYYY-MM-DD format
                    year, month, day = groups
                    try:
                        return date(int(year), int(month), int(day))
                    except ValueError:
                        continue

                elif len(groups) == 3 and any(
                    month in pattern for month in ["[A-Za-z]"]
                ):
                    # Month DD, YYYY format
                    month_str, day, year = groups
                    try:
                        month = DateUtil._get_month_number(month_str)
                        if month is None:
                            continue
                        return date(int(year), month, int(day))
                    except ValueError:
                        continue

        return None

