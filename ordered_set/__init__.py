"""
An OrderedSet is a custom MutableSet that remembers its order, so that every
entry has an index that can be looked up. It can also act like a Sequence.

Based on a recipe originally posted to ActiveState Recipes by Raymond Hettiger,
and released under the MIT license.
"""

import itertools as it
from typing import (
    Dict,
    Hashable,
    Iterable,
    Iterator,
    List,
    MutableSet,
    AbstractSet,
    Optional,
    Sequence,
    Container,
    Set,
    TypeVar,
    Union,
    overload,
    Sized,
    cast,
)

SLICE_ALL = slice(None)
__version__ = "4.1.1"


T = TypeVar("T")

# OrderedSetInitializer[T] represents any iterable that can be used to initialize
# or update an OrderedSet. Since AbstractSet and Sequence are both Iterable,
# we can simplify this to just Iterable[T].
OrderedSetInitializer = Iterable[T]
SizedSetLike = Union[AbstractSet[T], Sequence[T]]
SetLike = Union[SizedSetLike, Iterable[T]]


class OrderedSet(MutableSet[T], Sequence[T]):
    __slots__ = ("items", "map")
    """
    An OrderedSet is a custom MutableSet that remembers its order, so that
    every entry has an index that can be looked up.

    See documentation_examples.md for usage examples.
    """

    def __init__(self, initial: Optional[OrderedSetInitializer[T]] = None):
        self.items: List[T] = []
        self.map: Dict[T, int] = {}
        if initial is not None:
            self.update(initial)

    def __len__(self) -> int:
        """
        Returns the number of unique elements in the ordered set.
        See documentation_examples.md for usage examples.
        """
        return len(self.items)

    @overload
    def __getitem__(self, index: slice) -> "OrderedSet[T]": ...

    @overload
    def __getitem__(self, index: Iterable[int]) -> List[T]: ...

    @overload
    def __getitem__(self, index: int) -> T: ...

    # concrete implementation
    def __getitem__(self, index):
        """
        Get the item at a given index.

        If `index` is a slice, you will get back that slice of items, as a
        new OrderedSet.

        If `index` is a list or a similar iterable, you'll get a list of
        items corresponding to those indices. This is similar to NumPy's
        "fancy indexing". The result is not an OrderedSet because you may ask
        for duplicate indices, and the number of elements returned should be
        the number of elements asked for.

        See documentation_examples.md for usage examples.
        """
        if isinstance(index, slice):
            if index == SLICE_ALL:
                return self.copy()
            return self.__class__(self.items[index])
        elif isinstance(index, Iterable):
            return [self.items[i] for i in index]
        elif hasattr(index, "__index__"):
            return self.items[index]
        else:
            raise TypeError(f"Don't know how to index an OrderedSet by {index!r}")

    def copy(self) -> "OrderedSet[T]":
        """
        Return a shallow copy of this object.
        See documentation_examples.md for usage examples.
        """
        return self.__class__(self)

    # Define the gritty details of how an OrderedSet is serialized as a pickle.
    # We leave off type annotations, because the only code that should interact
    # with these is a generalized tool such as pickle.
    def __getstate__(self):
        if len(self) == 0:
            # In pickle, the state can't be an empty list.
            # We need to return a truthy value, or else __setstate__ won't be run.
            #
            # This could have been done more gracefully by always putting the state
            # in a tuple, but this way is backwards- and forwards- compatible with
            # previous versions of OrderedSet.
            return (None,)
        else:
            return list(self)

    def __setstate__(self, state):
        if state == (None,):
            self.__init__([])
        else:
            self.__init__(state)

    def __contains__(self, key: object) -> bool:
        """
        Test if the item is in this ordered set.
        See documentation_examples.md for usage examples.
        """
        return key in self.map

    def add(self, value: T) -> int:  # type: ignore[override]
        """
        Add `value` as an item to this OrderedSet, then return its index.

        If `value` is already in the OrderedSet, return the index it already
        had.

        See documentation_examples.md for usage examples.
        """
        if value not in self.map:
            self.map[value] = len(self.items)
            self.items.append(value)
        return self.map[value]

    def append(self, key: T) -> int:
        """
        Add `key` as an item to this OrderedSet, then return its index.
        This method calls self.add() to ensure proper inheritance behavior.

        See documentation_examples.md for usage examples.
        """
        return self.add(key)

    def update(self, *sequences: OrderedSetInitializer[T]) -> int:
        """
        Update the set with the given iterable sequence, then return the index
        of the last element inserted.

        See documentation_examples.md for usage examples.
        """
        item_index = 0
        for sequence in sequences:
            try:
                for item in sequence:
                    item_index = self.add(item)
            except TypeError:
                raise ValueError(
                    f"Argument needs to be an iterable, got {type(sequence)}"
                )
        return item_index

    @overload
    def index(self, key: Sequence[T]) -> List[int]: ...

    @overload
    def index(self, key: T) -> int: ...

    # concrete implementation
    def index(self, key: Union[T, Sequence[T]]):  # type: ignore[override]
        """
        Get the index of a given entry, raising an IndexError if it's not
        present.

        `key` can be an iterable of entries that is not a hashable (string, tuple, frozenset), in which case
        this returns a list of indices.

        See documentation_examples.md for usage examples.
        """
        if isinstance(key, Iterable) and not isinstance(key, Hashable):
            key_as_seq = cast(Sequence[T], key)
            return [self.index(subkey) for subkey in key_as_seq]
        # At this point, key must be of type T (single element, not a sequence)
        key_as_t = cast(T, key)
        return self.map[key_as_t]

    # Provide some compatibility with pd.Index
    get_loc = index
    get_indexer = index

    def pop(self, index: int = -1) -> T:
        """
        Remove and return item at index (default last).

        Raises KeyError if the set is empty.
        Raises IndexError if index is out of range.

        See documentation_examples.md for usage examples.
        """
        if not self.items:
            raise KeyError("Set is empty")

        elem = self.items[index]
        del self.items[index]

        # Rebuild the mapping to ensure indices are correct
        # This is necessary when removing from the middle of the set
        self.map = {item: i for i, item in enumerate(self.items)}

        return elem

    def __setitem__(self, index: int, value: T) -> None:
        """
        Replace the item at the given index with a new value.

        If the new value is already in the set at a different position,
        it will be removed from its old position first.

        Args:
            index: The index of the item to replace
            value: The new value to place at this index

        Raises:
            IndexError: If index is out of range
        """
        if not (-len(self.items) <= index < len(self.items)):
            raise IndexError("list index out of range")

        # Convert negative indices to positive
        if index < 0:
            index += len(self.items)

        old_value = self.items[index]

        # If the new value is already in the set, remove it first
        if value in self.map:
            old_index = self.map[value]
            if old_index == index:
                # Same value at same position, nothing to do
                return
            # Remove the value from its old position
            del self.items[old_index]
            # Adjust our target index if it was after the removed item
            if old_index < index:
                index -= 1

        # Update the item at the target index
        self.items[index] = value

        # Rebuild the mapping to ensure all indices are correct
        self.map = {item: i for i, item in enumerate(self.items)}

    def __delitem__(self, index: int) -> None:
        """
        Remove the item at the given index.

        Args:
            index: The index of the item to remove

        Raises:
            IndexError: If index is out of range
        """
        if not (-len(self.items) <= index < len(self.items)):
            raise IndexError("list index out of range")

        # Convert negative indices to positive
        if index < 0:
            index += len(self.items)

        # Remove the item
        del self.items[index]

        # Rebuild the mapping to ensure all indices are correct
        self.map = {item: i for i, item in enumerate(self.items)}

    def discard(self, value: T) -> None:
        """
        Remove an element.  Do not raise an exception if absent.

        The MutableSet mixin uses this to implement the .remove() method, which
        *does* raise an error when asked to remove a non-existent item.

        See documentation_examples.md for usage examples.
        """
        if value in self:
            i = self.map[value]
            del self.items[i]
            del self.map[value]
            for k, v in self.map.items():
                if v >= i:
                    self.map[k] = v - 1

    def clear(self) -> None:
        """
        Remove all items from this OrderedSet.
        """
        del self.items[:]
        self.map.clear()

    def __iter__(self) -> Iterator[T]:
        """
        Iterate over the items in order.
        See documentation_examples.md for usage examples.
        """
        return iter(self.items)

    def __reversed__(self) -> Iterator[T]:
        """
        Iterate over the items in reverse order.
        See documentation_examples.md for usage examples.
        """
        return reversed(self.items)

    def __repr__(self) -> str:
        if not self:
            return f"{self.__class__.__name__}()"
        return f"{self.__class__.__name__}({list(self)!r})"

    def __eq__(self, other: object) -> bool:
        """
        Returns true if the containers have the same items. If `other` is a
        Sequence, then order is checked, otherwise it is ignored.

        See documentation_examples.md for usage examples.
        """
        if isinstance(other, Sequence):
            # Check that this OrderedSet contains the same elements, in the
            # same order, as the other object.
            return list(self) == list(other)
        if not isinstance(other, Iterable):
            # If `other` is not iterable, it can't be equal to a set.
            return False
        try:
            other_as_set = set(other)
        except TypeError:
            # If `other` can't be converted into a set, it's not equal.
            return False
        else:
            return set(self) == other_as_set

    def union(self, *sets: OrderedSetInitializer[T]) -> "OrderedSet[T]":
        """
        Combines all unique items.
        Each items order is defined by its first appearance.

        See documentation_examples.md for usage examples.
        """
        cls: type = OrderedSet
        if isinstance(self, OrderedSet):
            cls = self.__class__
        items = it.chain(self, *sets)
        return cls(items)

    def __and__(self, other: SetLike[T]) -> "OrderedSet[T]":
        # the parent implementation of this is backwards
        return self.intersection(other)

    def intersection(self, *sets: OrderedSetInitializer[T]) -> "OrderedSet[T]":
        """
        Returns elements in common between all sets. Order is defined only
        by the first set.

        See documentation_examples.md for usage examples.
        """
        cls: type = OrderedSet
        items: OrderedSetInitializer[T] = self
        if isinstance(self, OrderedSet):
            cls = self.__class__
        if sets:
            common = set.intersection(*map(set, sets))
            items = (item for item in self if item in common)
        return cls(items)

    def difference(self, *sets: OrderedSetInitializer[T]) -> "OrderedSet[T]":
        """
        Returns all elements that are in this set but not the others.

        See documentation_examples.md for usage examples.
        """
        cls = self.__class__
        items: OrderedSetInitializer[T] = self
        if sets:
            other = set.union(*map(set, sets))
            items = (item for item in self if item not in other)
        return cls(items)

    def issubset(self, other: Iterable[object]) -> bool:
        """
        Report whether another set contains this set.

        See documentation_examples.md for usage examples.
        """
        if isinstance(other, Sized) and len(self) > len(
            other
        ):  # Fast check for obvious cases
            return False

        other_container: Container[object]
        if not isinstance(other, Container):
            other_container = set(other)
        else:
            other_container = other

        return all(item in other_container for item in self)

    def issuperset(self, other: Iterable[object]) -> bool:
        """
        Report whether this set contains another set.

        See documentation_examples.md for usage examples.
        """
        if isinstance(other, Sized) and len(self) < len(
            other
        ):  # Fast check for obvious cases
            return False
        return all(item in self for item in other)

    def symmetric_difference(self, other: OrderedSetInitializer[T]) -> "OrderedSet[T]":
        """
        Return the symmetric difference of two OrderedSets as a new set.
        That is, the new set will contain all elements that are in exactly
        one of the sets.

        Their order will be preserved, with elements from `self` preceding
        elements from `other`.

        See documentation_examples.md for usage examples.
        """
        cls: type = OrderedSet
        if isinstance(self, OrderedSet):
            cls = self.__class__
        diff1 = cls(self).difference(other)
        diff2 = cls(other).difference(self)
        return diff1.union(diff2)

    def _update_items(self, items: list) -> None:
        """
        Replace the 'items' list of this OrderedSet with a new one, updating
        self.map accordingly.
        """
        self.items = items
        self.map = {item: idx for (idx, item) in enumerate(items)}

    def difference_update(self, *sets: OrderedSetInitializer[T]) -> None:
        """
        Update this OrderedSet to remove items from one or more other sets.

        See documentation_examples.md for usage examples.
        """
        items_to_remove: Set[T] = set()
        for other in sets:
            items_as_set: Set[T] = set(other)
            items_to_remove |= items_as_set
        self._update_items([item for item in self.items if item not in items_to_remove])

    def intersection_update(self, other: OrderedSetInitializer[T]) -> None:
        """
        Update this OrderedSet to keep only items in another set, preserving
        their order in this set.

        See documentation_examples.md for usage examples.
        """
        other = set(other)
        self._update_items([item for item in self.items if item in other])

    def symmetric_difference_update(self, other: OrderedSetInitializer[T]) -> None:
        """
        Update this OrderedSet to remove items from another set, then
        add items from the other set that were not present in this set.

        See documentation_examples.md for usage examples.
        """
        items_to_add = [item for item in other if item not in self]
        items_to_remove = set(other)
        self._update_items(
            [item for item in self.items if item not in items_to_remove] + items_to_add
        )
