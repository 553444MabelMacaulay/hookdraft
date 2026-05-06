"""Tag management for webhook requests."""
from typing import List, Optional


def add_tag(tags: List[str], tag: str) -> List[str]:
    """Return a new tag list with the given tag added (deduped)."""
    tag = tag.strip().lower()
    if not tag:
        raise ValueError("Tag must not be empty")
    if tag not in tags:
        return tags + [tag]
    return list(tags)


def remove_tag(tags: List[str], tag: str) -> List[str]:
    """Return a new tag list with the given tag removed."""
    tag = tag.strip().lower()
    return [t for t in tags if t != tag]


def filter_by_tag(records, tag: str) -> list:
    """Filter a list of RequestRecord objects by a tag."""
    tag = tag.strip().lower()
    return [r for r in records if tag in r.tags]


def filter_by_any_tag(records, tags: List[str]) -> list:
    """Return records that have at least one of the given tags."""
    tag_set = {t.strip().lower() for t in tags}
    return [r for r in records if tag_set.intersection(r.tags)]


def all_tags(records) -> List[str]:
    """Return a sorted list of all unique tags across all records."""
    seen = set()
    for r in records:
        seen.update(r.tags)
    return sorted(seen)
