import collections
import itertools as it
import operator
import pickle
import random
import sys

import pytest

from ordered_set import OrderedSet


def test_pickle():
    set1 = OrderedSet("abracadabra")
    roundtrip = pickle.loads(pickle.dumps(set1))
    assert roundtrip == set1


def test_empty_pickle():
    empty_oset = OrderedSet()
    empty_roundtrip = pickle.loads(pickle.dumps(empty_oset))
    assert empty_roundtrip == empty_oset


def test_order():
    set1 = OrderedSet("abracadabra")
    assert len(set1) == 5
    assert set1 == OrderedSet(["a", "b", "r", "c", "d"])
    assert list(reversed(set1)) == ["d", "c", "r", "b", "a"]


def test_binary_operations():
    set1 = OrderedSet("abracadabra")
    set2 = OrderedSet("simsalabim")
    assert set1 != set2

    assert set1 & set2 == OrderedSet(["a", "b"])
    assert set1 | set2 == OrderedSet(["a", "b", "r", "c", "d", "s", "i", "m", "l"])
    assert set1 - set2 == OrderedSet(["r", "c", "d"])


def test_indexing():
    set1 = OrderedSet("abracadabra")
    assert set1[:] == set1
    assert set1.copy() == set1
    assert set1 is set1
    assert set1[:] is not set1
    assert set1.copy() is not set1

    assert set1[[1, 2]] == ["b", "r"]
    assert set1[1:3] == OrderedSet(["b", "r"])
    assert set1.index("b") == 1
    assert set1.index(["b", "r"]) == [1, 2]
    with pytest.raises(KeyError):
        set1.index("br")

    set2 = OrderedSet((("a", "b"), frozenset(("c", "d")), "efg"))
    assert set2.index(("a", "b")) == 0
    assert set2.index(frozenset(("c", "d"))) == 1
    assert set2.index("efg") == 2
    assert set2.index([frozenset(("c", "d")), ("a", "b")]) == [1, 0]
    assert set2.index(OrderedSet([frozenset(("c", "d")), ("a", "b")])) == [1, 0]
    with pytest.raises(KeyError):
        set2.index(["a", "b"])  # type: ignore[arg-type]

    # Test for Issue #95: frozenset should be treated as atomic, not iterated over
    set3 = OrderedSet([frozenset([1, 2])])
    assert set3.index(frozenset([1, 2])) == 0


def test_append_inheritance():
    """Test for Issue #94: append() should call overridden add() method in subclasses"""

    class CustomOrderedSet(OrderedSet):
        def __init__(self):
            super().__init__()
            self.add_called = False
            self.append_called = False

        def add(self, value):
            self.add_called = True
            return super().add(value)

    custom_set = CustomOrderedSet()

    # Test that append() calls the overridden add() method
    custom_set.append("test")
    assert custom_set.add_called, "append() should call the overridden add() method"
    assert "test" in custom_set
    assert custom_set.index("test") == 0


def test_pop_index_consistency():
    """Test for Issue #83: pop() with non-default index should maintain index consistency"""

    # Test the exact scenario from the issue
    a = OrderedSet(["a", "b", "c"])
    assert a.index("b") == 1

    # Pop the first element
    popped = a.pop(0)
    assert popped == "a"

    # After popping "a", "b" should now be at index 0
    assert a.index("b") == 0
    assert a[0] == "b"
    assert a[1] == "c"

    # Test popping from the middle
    b = OrderedSet(["x", "y", "z", "w"])
    assert b.index("z") == 2
    assert b.index("w") == 3

    # Pop "y" (index 1)
    popped = b.pop(1)
    assert popped == "y"

    # Indices should be updated
    assert b.index("z") == 1  # was 2, now 1
    assert b.index("w") == 2  # was 3, now 2
    assert b[1] == "z"
    assert b[2] == "w"

    # Test that pop(-1) still works efficiently
    c = OrderedSet([1, 2, 3, 4, 5])
    last = c.pop()  # default is -1
    assert last == 5
    assert list(c) == [1, 2, 3, 4]


def test_item_assignment():
    """Test for Issue #79: Support item assignment (s[index] = value)"""

    # Basic assignment
    s = OrderedSet(["foo"])
    assert s[0] == "foo"
    s[0] = "bar"
    assert s[0] == "bar"
    assert list(s) == ["bar"]

    # Assignment in multi-item set
    s = OrderedSet(["a", "b", "c"])
    s[1] = "x"
    assert list(s) == ["a", "x", "c"]
    assert s.index("x") == 1

    # Assignment with existing value (should move it)
    s = OrderedSet(["a", "b", "c"])
    s[0] = "c"  # Move 'c' from index 2 to index 0
    assert list(s) == ["c", "b"]
    assert s.index("c") == 0

    # Assignment with same value at same position (no-op)
    s = OrderedSet(["a", "b", "c"])
    s[1] = "b"
    assert list(s) == ["a", "b", "c"]

    # Negative indices
    s = OrderedSet(["a", "b", "c"])
    s[-1] = "z"
    assert list(s) == ["a", "b", "z"]

    # Index out of range
    s = OrderedSet(["a"])
    with pytest.raises(IndexError):
        s[5] = "x"
    with pytest.raises(IndexError):
        s[-5] = "x"


def test_item_deletion():
    """Test for Issue #79: Support item deletion (del s[index])"""

    # Basic deletion
    s = OrderedSet(["a", "b", "c"])
    del s[0]
    assert list(s) == ["b", "c"]
    assert s.index("b") == 0
    assert s.index("c") == 1

    # Delete from middle
    s = OrderedSet(["a", "b", "c", "d"])
    del s[1]  # Remove 'b'
    assert list(s) == ["a", "c", "d"]
    assert s.index("c") == 1
    assert s.index("d") == 2

    # Delete last item
    s = OrderedSet(["a", "b", "c"])
    del s[-1]
    assert list(s) == ["a", "b"]

    # Delete from single-item set
    s = OrderedSet(["only"])
    del s[0]
    assert list(s) == []
    assert len(s) == 0

    # Index out of range
    s = OrderedSet(["a"])
    with pytest.raises(IndexError):
        del s[5]
    with pytest.raises(IndexError):
        del s[-5]

    # Empty set
    s = OrderedSet()
    with pytest.raises(IndexError):
        del s[0]


def test_update_with_iterables():
    """Test for Issue #85: update() should accept any Iterable, including generators"""

    # Test with generator
    s = OrderedSet([1, 2])
    gen = (x for x in [3, 4, 5])
    s.update(gen)
    assert list(s) == [1, 2, 3, 4, 5]

    # Test with multiple iterables
    s = OrderedSet()
    s.update([1, 2], (3, 4), {5, 6})
    assert len(s) == 6
    assert 1 in s and 2 in s and 3 in s and 4 in s and 5 in s and 6 in s

    # Test with string (iterable)
    s = OrderedSet()
    s.update("abc")
    assert list(s) == ["a", "b", "c"]

    # Test with range (iterable)
    s = OrderedSet()
    s.update(range(3))
    assert list(s) == [0, 1, 2]


class FancyIndexTester:
    """
    Make sure we can index by a NumPy ndarray, without having to import
    NumPy.
    """

    def __init__(self, indices):
        self.indices = indices

    def __iter__(self):
        return iter(self.indices)

    def __index__(self):
        raise TypeError("NumPy arrays have weird __index__ methods")

    def __eq__(self, other):
        # Emulate NumPy being fussy about the == operator
        raise TypeError


def test_fancy_index_class():
    set1 = OrderedSet("abracadabra")
    indexer = FancyIndexTester([1, 0, 4, 3, 0, 2])
    items = set1[indexer]  # type: ignore
    assert "".join(items) == "badcar"


def test_pandas_compat():
    set1 = OrderedSet("abracadabra")
    assert set1.get_loc("b") == 1
    assert set1.get_indexer(["b", "r"]) == [1, 2]


def test_tuples():
    set1 = OrderedSet()
    tup = ("tuple", 1)
    set1.add(tup)
    assert set1.index(tup) == 0
    assert set1[0] == tup


def test_remove():
    set1 = OrderedSet("abracadabra")

    set1.remove("a")
    set1.remove("b")

    assert set1 == OrderedSet("rcd")
    assert set1[0] == "r"
    assert set1[1] == "c"
    assert set1[2] == "d"

    assert set1.index("r") == 0
    assert set1.index("c") == 1
    assert set1.index("d") == 2

    assert "a" not in set1
    assert "b" not in set1
    assert "r" in set1

    # Make sure we can .discard() something that's already gone, plus
    # something that was never there
    set1.discard("a")
    set1.discard("a")


def test_remove_error():
    # If we .remove() an element that's not there, we get a KeyError
    set1 = OrderedSet("abracadabra")
    with pytest.raises(KeyError):
        set1.remove("z")


def test_clear():
    set1 = OrderedSet("abracadabra")
    set1.clear()

    assert len(set1) == 0
    assert set1 == OrderedSet()


def test_update():
    set1 = OrderedSet("abcd")
    result = set1.update("efgh")

    assert result == 7
    assert len(set1) == 8
    assert "".join(set1) == "abcdefgh"

    set2 = OrderedSet("abcd")
    result = set2.update("cdef")
    assert result == 5
    assert len(set2) == 6
    assert "".join(set2) == "abcdef"


def test_pop():
    set1 = OrderedSet("ab")
    elem = set1.pop()

    assert elem == "b"
    elem = set1.pop()

    assert elem == "a"

    pytest.raises(KeyError, set1.pop)


def test_getitem_type_error():
    set1 = OrderedSet("ab")
    with pytest.raises(TypeError):
        set1["a"]  # type: ignore


def test_update_value_error():
    set1 = OrderedSet("ab")
    with pytest.raises(ValueError):
        # noinspection PyTypeChecker
        set1.update(3)  # type: ignore


def test_empty_repr():
    set1 = OrderedSet()
    assert repr(set1) == "OrderedSet()"


def test_eq_wrong_type():
    set1 = OrderedSet()
    assert set1 != 2


def test_ordered_equality():
    # Ordered set checks order against sequences.
    assert OrderedSet([1, 2]) == OrderedSet([1, 2])
    assert OrderedSet([1, 2]) == [1, 2]
    assert OrderedSet([1, 2]) == (1, 2)
    assert OrderedSet([1, 2]) == collections.deque([1, 2])


def test_ordered_inequality():
    # Ordered set checks order against sequences.
    assert OrderedSet([1, 2]) != OrderedSet([2, 1])

    assert OrderedSet([1, 2]) != [2, 1]
    assert OrderedSet([1, 2]) != [2, 1, 1]

    assert OrderedSet([1, 2]) != (2, 1)
    assert OrderedSet([1, 2]) != (2, 1, 1)

    # Note: in Python 2.7 deque does not inherit from Sequence, but __eq__
    # contains an explicit check for this case for python 2/3 compatibility.
    assert OrderedSet([1, 2]) != collections.deque([2, 1])
    assert OrderedSet([1, 2]) != collections.deque([2, 2, 1])


def test_comparisons():
    # Comparison operators on sets actually test for subset and superset.
    assert OrderedSet([1, 2]) < OrderedSet([1, 2, 3])
    assert OrderedSet([1, 2]) > OrderedSet([1])

    # MutableSet subclasses aren't comparable to set on 3.3.
    if tuple(sys.version_info) >= (3, 4):
        assert OrderedSet([1, 2]) > {1}


def test_unordered_equality():
    # Unordered set checks order against non-sequences.
    assert OrderedSet([1, 2]) == {1, 2}
    assert OrderedSet([1, 2]) == frozenset([2, 1])

    assert OrderedSet([1, 2]) == {1: "a", 2: "b"}
    assert OrderedSet([1, 2]) == {1: 1, 2: 2}.keys()
    assert OrderedSet([1, 2]) == {1: 1, 2: 2}.values()

    # Corner case: OrderedDict is not a Sequence, so we don't check for order,
    # even though it does have the concept of order.
    assert OrderedSet([1, 2]) == collections.OrderedDict([(2, 2), (1, 1)])

    # Corner case: We have to treat iterators as unordered because there
    # is nothing to distinguish an ordered and unordered iterator
    assert OrderedSet([1, 2]) == iter([1, 2])
    assert OrderedSet([1, 2]) == iter([2, 1])
    assert OrderedSet([1, 2]) == iter([2, 1, 1])


def test_unordered_inequality():
    assert OrderedSet([1, 2]) != set([])
    assert OrderedSet([1, 2]) != frozenset([2, 1, 3])

    assert OrderedSet([1, 2]) != {2: "b"}
    assert OrderedSet([1, 2]) != {1: 1, 4: 2}.keys()
    assert OrderedSet([1, 2]) != {1: 1, 2: 3}.values()

    # Corner case: OrderedDict is not a Sequence, so we don't check for order,
    # even though it does have the concept of order.
    assert OrderedSet([1, 2]) != collections.OrderedDict([(2, 2), (3, 1)])


def allsame_(iterable, eq=operator.eq):
    """returns True of all items in iterable equal each other"""
    iter_ = iter(iterable)
    try:
        first = next(iter_)
    except StopIteration:
        return True
    return all(eq(first, item) for item in iter_)


def check_results_(results, datas, name):
    """
    helper for binary operator tests.

    check that all results have the same value, but are different items.
    data and name are used to indicate what sort of tests is run.
    """
    if not allsame_(results):
        raise AssertionError(
            "Not all same {} for {} with datas={}".format(results, name, datas)
        )
    for a, b in it.combinations(results, 2):
        if not isinstance(a, (bool, int)):
            assert a is not b, name + " should all be different items"


def _operator_consistency_testdata():
    """
    Predefined and random data used to test operator consistency.
    """
    # test case 1
    data1 = OrderedSet([5, 3, 1, 4])
    data2 = OrderedSet([1, 4])
    yield data1, data2

    # first set is empty
    data1 = OrderedSet([])
    data2 = OrderedSet([3, 1, 2])
    yield data1, data2

    # second set is empty
    data1 = OrderedSet([3, 1, 2])
    data2 = OrderedSet([])
    yield data1, data2

    # both sets are empty
    data1 = OrderedSet([])
    data2 = OrderedSet([])
    yield data1, data2

    # random test cases
    rng = random.Random(0)
    a, b = 20, 20
    for _ in range(10):
        data1 = OrderedSet(rng.randint(0, a) for _ in range(b))
        data2 = OrderedSet(rng.randint(0, a) for _ in range(b))
        yield data1, data2
        yield data2, data1


def test_operator_consistency_isect():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1.copy()
        result1.intersection_update(data2)
        result2 = data1 & data2
        result3 = data1.intersection(data2)
        check_results_([result1, result2, result3], datas=(data1, data2), name="isect")


def test_operator_consistency_difference():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1.copy()
        result1.difference_update(data2)
        result2 = data1 - data2
        result3 = data1.difference(data2)
        check_results_(
            [result1, result2, result3], datas=(data1, data2), name="difference"
        )


def test_operator_consistency_xor():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1.copy()
        result1.symmetric_difference_update(data2)
        result2 = data1 ^ data2
        result3 = data1.symmetric_difference(data2)
        check_results_([result1, result2, result3], datas=(data1, data2), name="xor")


def test_operator_consistency_union():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1.copy()
        result1.update(data2)
        result2 = data1 | data2
        result3 = data1.union(data2)
        check_results_([result1, result2, result3], datas=(data1, data2), name="union")


def test_operator_consistency_subset():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1 <= data2
        result2 = data1.issubset(data2)
        result3 = set(data1).issubset(set(data2))
        check_results_([result1, result2, result3], datas=(data1, data2), name="subset")


def test_operator_consistency_superset():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1 >= data2
        result2 = data1.issuperset(data2)
        result3 = set(data1).issuperset(set(data2))
        check_results_(
            [result1, result2, result3], datas=(data1, data2), name="superset"
        )


def test_operator_consistency_disjoint():
    for data1, data2 in _operator_consistency_testdata():
        result1 = data1.isdisjoint(data2)
        result2 = len(data1.intersection(data2)) == 0
        check_results_([result1, result2], datas=(data1, data2), name="disjoint")


def test_bitwise_and_consistency():
    # Specific case that was failing without explicit __and__ definition
    data1 = OrderedSet([12, 13, 1, 8, 16, 15, 9, 11, 18, 6, 4, 3, 19, 17])
    data2 = OrderedSet([19, 4, 9, 3, 2, 10, 15, 17, 11, 13, 20, 6, 14, 16, 8])
    result1 = data1.copy()
    result1.intersection_update(data2)
    # This requires a custom & operation apparently
    result2 = data1 & data2
    result3 = data1.intersection(data2)
    check_results_([result1, result2, result3], datas=(data1, data2), name="isect")
