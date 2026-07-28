"""Data models for /v1/rank.

Annotations document expected types but DO NOT enforce them at runtime.
@dataclasess.dataclass generates __init__, __repr__, __eq__, etc.,
but does not check that passed values match the annotations.

See demo_annotations_dont_validate.py
"""

from dataclasses import dataclass


@dataclass
class RankItem:
    """A single item to rank."""
    label: str   # type annotation is documentation only
    score: float  # type annotation is documentation only


@dataclass
class RankRequest:
    """Request body for POST /v1/rank."""
    items: list[RankItem]
    limit: int | None = None
