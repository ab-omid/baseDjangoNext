from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Answer:
    answer: Optional[Any]
    justification: Optional[str]
