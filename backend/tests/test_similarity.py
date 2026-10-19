
import pytest

from app.retrieval.similarity import cosine_similarity


def test_identical_vectors():
    score = cosine_similarity([1, 0], [1, 0])

    assert score == pytest.approx(1.0)


def test_orthogonal_vectors():
    score = cosine_similarity([1, 0], [0, 1])

    assert score == pytest.approx(0.0)


def test_opposite_vectors():
    score = cosine_similarity([1, 0], [-1, 0])

    assert score == pytest.approx(-1.0)


def test_different_dimensions():
    with pytest.raises(ValueError):
        cosine_similarity([1, 2], [1, 2, 3])


def test_empty_vectors():
    with pytest.raises(ValueError):
        cosine_similarity([], [])


def test_zero_vector():
    with pytest.raises(ValueError):
        cosine_similarity([0, 0], [1, 0])
