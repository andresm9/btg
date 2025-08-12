import logging
from typing import Any

from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import CoreSchema

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)


