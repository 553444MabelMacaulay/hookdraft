"""Tests for hookdraft.clustering."""

import pytest
from hookdraft.clustering import (
    add_to_cluster,
    remove_from_cluster,
    get_clusters,
    is_in_cluster,
    cluster_count,
    filter_by_cluster,
    group_by_cluster,
)


def _rec(**kwargs):
    return dict(kwargs)


def test_get_clusters_empty_by_default():
    r = _rec()
    assert get_clusters(r) == []


def test_cluster_count_zero_by_default():
    r = _rec()
    assert cluster_count(r) == 0


def test_is_in_cluster_false_by_default():
    r = _rec()
    assert is_in_cluster(r, "alpha") is False


def test_add_to_cluster_basic():
    r = _rec()
    add_to_cluster(r, "alpha")
    assert "alpha" in get_clusters(r)


def test_add_to_cluster_normalises_case():
    r = _rec()
    add_to_cluster(r, "Alpha")
    assert "alpha" in get_clusters(r)


def test_add_to_cluster_deduped():
    r = _rec()
    add_to_cluster(r, "alpha")
    add_to_cluster(r, "alpha")
    assert get_clusters(r).count("alpha") == 1


def test_add_to_cluster_multiple():
    r = _rec()
    add_to_cluster(r, "alpha")
    add_to_cluster(r, "beta")
    assert cluster_count(r) == 2


def test_add_to_cluster_empty_name_raises():
    r = _rec()
    with pytest.raises(ValueError):
        add_to_cluster(r, "")


def test_add_to_cluster_whitespace_only_raises():
    r = _rec()
    with pytest.raises(ValueError):
        add_to_cluster(r, "   ")


def test_add_to_cluster_too_long_raises():
    r = _rec()
    with pytest.raises(ValueError):
        add_to_cluster(r, "x" * 65)


def test_remove_from_cluster_basic():
    r = _rec()
    add_to_cluster(r, "alpha")
    remove_from_cluster(r, "alpha")
    assert get_clusters(r) == []


def test_remove_from_cluster_idempotent():
    r = _rec()
    remove_from_cluster(r, "alpha")  # should not raise
    assert get_clusters(r) == []


def test_is_in_cluster_true_after_add():
    r = _rec()
    add_to_cluster(r, "gamma")
    assert is_in_cluster(r, "gamma") is True


def test_filter_by_cluster():
    r1 = _rec()
    r2 = _rec()
    add_to_cluster(r1, "alpha")
    add_to_cluster(r2, "beta")
    result = filter_by_cluster([r1, r2], "alpha")
    assert result == [r1]


def test_filter_by_cluster_empty_name_raises():
    with pytest.raises(ValueError):
        filter_by_cluster([], "")


def test_group_by_cluster():
    r1 = _rec()
    r2 = _rec()
    r3 = _rec()
    add_to_cluster(r1, "alpha")
    add_to_cluster(r2, "alpha")
    add_to_cluster(r3, "beta")
    groups = group_by_cluster([r1, r2, r3])
    assert set(groups.keys()) == {"alpha", "beta"}
    assert len(groups["alpha"]) == 2
    assert len(groups["beta"]) == 1


def test_group_by_cluster_record_in_multiple_clusters():
    r = _rec()
    add_to_cluster(r, "alpha")
    add_to_cluster(r, "beta")
    groups = group_by_cluster([r])
    assert r in groups["alpha"]
    assert r in groups["beta"]
