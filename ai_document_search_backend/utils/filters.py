from typing import Literal

from pydantic import BaseModel


class Filter(BaseModel):
    property_name: Literal["isin", "shortname"]
    values: list[str]


def construct_and_filter(filters: list[Filter]) -> dict:
    and_filter = {
        "operator": "And",
        "operands": [construct_or_filter(filter) for filter in filters if len(filter.values) > 0],
    }
    if len(and_filter["operands"]) == 0:
        return {}
    return and_filter


def construct_or_filter(filter: Filter) -> dict:
    or_filter = {
        "operator": "Or",
        "operands": [
            {
                "path": [filter.property_name],
                "operator": "Equal",
                "valueText": value,
            }
            for value in filter.values
        ],
    }
    return or_filter
