"""Pydantic model's str attribute lowercasing module."""
from pydantic import BaseModel


def lower_str_attrs(obj: BaseModel):
    """Lowercase str attributes of a pydantic model."""
    for k, v in obj.dict().items():
        attr = getattr(obj, k)
        if isinstance(attr, str):
            setattr(obj, k, v.strip().lower())
