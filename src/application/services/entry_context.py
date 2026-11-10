"""Entry payload shared by the polling and dispatch layers."""

from __future__ import annotations

from dataclasses import dataclass

from ...domain.entities.content_types import LayoutFragment


@dataclass(frozen=True, slots=True)
class EntryContentContext:
    """Raw entry payload before text formatting for one subscription."""

    title: str
    summary: str
    content: str
    link: str
    author: str
    feed_title: str
    feed_link: str
    raw_xml: str = ""
    media_urls: tuple[str, ...] = ()
    media_items: tuple[tuple[str, str], ...] = ()
    layout: tuple[LayoutFragment, ...] = ()
