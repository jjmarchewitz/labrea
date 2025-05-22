import pytest

from labrea.coalesce import Coalesce
from labrea.exceptions import EvaluationError, KeyNotFoundError
from labrea.option import Option


def test_coalesce():
    a = Option("A")
    b = Option("B")

    c = Coalesce(a, b)

    assert c({"A": "Hello"}) == "Hello"
    assert c({"B": "World!"}) == "World!"
    assert c({"A": "Hello", "B": "World!"}) == "Hello"
    assert c({"B": "World!", "C": "foo"}) == "World!"

    assert c.evaluate_options({"A": "Hello"}) == {"A": "Hello"}
    assert c.evaluate_options({"B": "World!"}) == {"B": "World!"}
    assert c.evaluate_options({"A": "Hello", "B": "World!"}) == {"A": "Hello"}
    assert c.evaluate_options({"B": "World!", "C": "foo"}) == {"B": "World!"}

    with pytest.raises(EvaluationError):
        c({})

    with pytest.raises(KeyNotFoundError):
        c.validate({})

    with pytest.raises(KeyNotFoundError):
        c.keys({})

    assert c.explain() == {"B"}


def test_repr():
    assert (
        repr(Coalesce(Option("A"), Option("B"))) == "Coalesce(Option('A'), Option('B'))"
    )


def test_init():
    with pytest.raises(TypeError):
        Coalesce()
