"""Clustering: group records into named clusters for batch analysis."""

from __future__ import annotations

from typing import List, Optional


def _validate_cluster_name(name: str) -> str:
    name = name.strip().lower()
    if not name:
        raise ValueError("Cluster name must not be empty.")
    if len(name) > 64:
        raise ValueError("Cluster name must not exceed 64 characters.")
    return name


def add_to_cluster(record: dict, cluster_name: str) -> None:
    """Add a record to a named cluster. Deduplicates entries."""
    cluster_name = _validate_cluster_name(cluster_name)
    clusters: List[str] = record.setdefault("clusters", [])
    if cluster_name not in clusters:
        clusters.append(cluster_name)


def remove_from_cluster(record: dict, cluster_name: str) -> None:
    """Remove a record from a named cluster. No-op if not a member."""
    cluster_name = _validate_cluster_name(cluster_name)
    clusters: List[str] = record.get("clusters", [])
    record["clusters"] = [c for c in clusters if c != cluster_name]


def get_clusters(record: dict) -> List[str]:
    """Return the list of clusters this record belongs to."""
    return list(record.get("clusters", []))


def is_in_cluster(record: dict, cluster_name: str) -> bool:
    """Return True if the record belongs to the given cluster."""
    cluster_name = _validate_cluster_name(cluster_name)
    return cluster_name in record.get("clusters", [])


def cluster_count(record: dict) -> int:
    """Return the number of clusters the record belongs to."""
    return len(record.get("clusters", []))


def filter_by_cluster(records: List[dict], cluster_name: str) -> List[dict]:
    """Return only records that belong to the given cluster."""
    cluster_name = _validate_cluster_name(cluster_name)
    return [r for r in records if cluster_name in r.get("clusters", [])]


def group_by_cluster(records: List[dict]) -> dict:
    """Return a mapping of cluster_name -> list of records."""
    result: dict = {}
    for record in records:
        for cluster in record.get("clusters", []):
            result.setdefault(cluster, []).append(record)
    return result
