from robusta.api import ActionParams
from typing import List

class LogFilterParams(ActionParams):
    keywords: List[str]
