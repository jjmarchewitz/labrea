import pytest

from labrea.exceptions import EvaluationError, KeyNotFoundError
from labrea.option import Option
from labrea.types import Evaluatable, Value


def test_value():
    value = Value(42)
    assert value.evaluate({}) == value() == 42
    assert value.validate({}) is None
    assert value.keys({}) == set()
    assert value.explain() == value.explain({}) == set()
    assert value.evaluate_options({"A": 1}) == {}
    assert repr(value) == "Value(42)"
    assert value == value
    assert value != Value(43)

    class Uncopyable:
        def __deepcopy__(self, memo):
            raise NotImplementedError("Cannot copy this.")

    uncopyable = Uncopyable()

    assert Value(uncopyable).evaluate({}) is uncopyable


def test_unit():
    assert Evaluatable.unit(1)() == 1


@pytest.mark.parametrize(
    "wrapper,method",
    [
        (wrapper, method)
        for wrapper in (Value, lambda x: x)
        for method in ("apply", "rshift")
    ],
)
def test_apply(wrapper, method):
    # JAKE: should I add to any other cases in this file?
    value = Value(42)

    def incr(x):
        return x + 1

    if method == "apply":
        apply = value.apply(wrapper(incr))
    else:
        apply = value >> wrapper(incr)

    assert apply.evaluate({}) == 43
    assert apply.validate({}) is None
    assert apply.keys({}) == set()
    assert apply.explain() == set()
    assert repr(apply) == f"Value(42).apply(Value({repr(incr)}))"


def test_bind():
    value = Value(42)

    def incr(x):
        return Value(x + 1)

    bind = value.bind(incr)
    assert bind.evaluate({}) == 43
    assert bind.validate({}) is None
    assert bind.keys({}) == set()
    assert bind.explain() == set()
    assert repr(bind) == f"Value(42).bind({repr(incr)})"

    option_a = Option("A")

    def choose(bool_arg: bool) -> Option:
        return Option("X") if bool_arg else Option("Y")

    bind = option_a.bind(choose)
    select_x = {"A": True, "X": 1, "Y": 2, "Z": 3}
    select_y = {"A": False, "X": 1, "Y": 2, "Z": 3}

    assert bind.evaluate(select_x) == 1
    assert bind.evaluate(select_y) == 2
    assert bind.evaluate_options(select_x) == {"A": True, "X": 1}
    assert bind.evaluate_options(select_y) == {"A": False, "Y": 2}
    # other methods are already validated above


def test_type_error():
    with pytest.raises(TypeError):
        Value(42).bind(42)

    with pytest.raises(TypeError):
        Value(42).apply(42)


def test_error_str():
    assert (
        str(EvaluationError("message", Value(1))) == "Originating in Value(1) | message"
    )
    assert (
        str(KeyNotFoundError("key", Value(1)))
        == "Originating in Value(1) | Key 'key' not found"
    )


def test_fingerprint():
    value = Value(42)
    option = Option("A")

    # No label
    assert value.fingerprint({}) == value.fingerprint({"A": 1})
    assert value.fingerprint({"A": 1}) != option.fingerprint({"A": 1})
    assert option.fingerprint({"A": 1}) == option.fingerprint({"A": 1})
    assert option.fingerprint({"A": 1}) != option.fingerprint({"A": 2})
    assert option.fingerprint({"A": 1}) == option.fingerprint({"A": 1, "V": 2})

    l1 = "LABEL1"
    l2 = "LABEL2"

    # Label 1
    assert value.fingerprint({}, cache_label=l1) == value.fingerprint(
        {"A": 1}, cache_label=l1
    )
    assert value.fingerprint({"A": 1}, cache_label=l1) != option.fingerprint(
        {"A": 1}, cache_label=l1
    )
    assert option.fingerprint({"A": 1}, cache_label=l1) == option.fingerprint(
        {"A": 1}, cache_label=l1
    )
    assert option.fingerprint({"A": 1}, cache_label=l1) != option.fingerprint(
        {"A": 2}, cache_label=l1
    )
    assert option.fingerprint({"A": 1}, cache_label=l1) == option.fingerprint(
        {"A": 1, "V": 2}, cache_label=l1
    )

    # Label 1 != Label 2
    assert value.fingerprint({}, cache_label=l1) != value.fingerprint(
        {"A": 1}, cache_label=l2
    )
    assert value.fingerprint({"A": 1}, cache_label=l1) != option.fingerprint(
        {"A": 1}, cache_label=l2
    )
    assert option.fingerprint({"A": 1}, cache_label=l1) != option.fingerprint(
        {"A": 1}, cache_label=l2
    )
    assert option.fingerprint({"A": 1}, cache_label=l1) != option.fingerprint(
        {"A": 2}, cache_label=l2
    )
    assert option.fingerprint({"A": 1}, cache_label=l1) != option.fingerprint(
        {"A": 1, "V": 2}, cache_label=l2
    )


def test_result():
    option = Option("A")
    assert option.result is option
