from dataclasses import dataclass
from typing import Dict, List, Any, Union
from datetime import datetime


@dataclass
class ItemModel:
    key: str
    spider: str
    created: Union[datetime, None]
    attributes: Dict[Any, Any] = None
    formatted: str = None


@dataclass
class SpiderModel:
    name: str
    params: Dict[str, str] = None
    settings: Dict[str, str] = None


@dataclass
class SpiderStatsModel:
    spider: str
    start_time: datetime
    finish_time: datetime
    elapsed_time: float
    item_scraped_count: int = 0
    item_dropped_count: int = 0
    request_bytes: int = 0
    response_bytes: int = 0
    http_requests: int = 0
    http_success_requests: int = 0
    http_error_requests: int = 0


@dataclass
class JobModel:
    id: str
    trigger: str
    spider: SpiderModel
    next_run: datetime
    statistics: SpiderStatsModel = None
