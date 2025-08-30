# OrderedSet Documentation Examples

This file contains all the code examples extracted from the OrderedSet class docstrings, organized by functionality.

## Basic Usage

### Creating an OrderedSet

```python
>>> OrderedSet([1, 1, 2, 3, 2])
OrderedSet([1, 2, 3])
```

### Length Operations

```python
>>> len(OrderedSet([]))
0
>>> len(OrderedSet([1, 2]))
2
```

### Membership Testing

```python
>>> 1 in OrderedSet([1, 3, 2])
True
>>> 5 in OrderedSet([1, 3, 2])
False
```

## Indexing and Accessing Elements

### Getting Items by Index

```python
>>> oset = OrderedSet([1, 2, 3])
>>> oset[1]
2
```

### Finding Index of Elements

```python
>>> oset = OrderedSet([1, 2, 3])
>>> oset.index(2)
1
```

## Copying

```python
>>> this = OrderedSet([1, 2, 3])
>>> other = this.copy()
>>> this == other
True
>>> this is other
False
```

## Adding Elements

### Adding Single Elements

```python
>>> oset = OrderedSet()
>>> oset.append(3)
0
>>> print(oset)
OrderedSet([3])
```

### Updating with Multiple Elements

```python
>>> oset = OrderedSet([1, 2, 3])
>>> oset.update([3, 1, 5, 1, 4])
4
>>> print(oset)
OrderedSet([1, 2, 3, 5, 4])
```

## Removing Elements

### Popping Elements

```python
>>> oset = OrderedSet([1, 2, 3])
>>> oset.pop()
3
```

### Discarding Elements

```python
>>> oset = OrderedSet([1, 2, 3])
>>> oset.discard(2)
>>> print(oset)
OrderedSet([1, 3])
>>> oset.discard(2)
>>> print(oset)
OrderedSet([1, 3])
```

## Iteration

### Forward Iteration

```python
>>> list(iter(OrderedSet([1, 2, 3])))
[1, 2, 3]
```

### Reverse Iteration

```python
>>> list(reversed(OrderedSet([1, 2, 3])))
[3, 2, 1]
```

## Comparison Operations

### Equality Testing

```python
>>> oset = OrderedSet([1, 3, 2])
>>> oset == [1, 3, 2]
True
>>> oset == [1, 2, 3]
False
>>> oset == [2, 3]
False
>>> oset == OrderedSet([3, 2, 1])
False
```

## Set Operations

### Union

```python
>>> oset = OrderedSet.union(OrderedSet([3, 1, 4, 1, 5]), [1, 3], [2, 0])
>>> print(oset)
OrderedSet([3, 1, 4, 5, 2, 0])
>>> oset.union([8, 9])
OrderedSet([3, 1, 4, 5, 2, 0, 8, 9])
>>> oset | {10}
OrderedSet([3, 1, 4, 5, 2, 0, 10])
```

### Intersection

```python
>>> oset = OrderedSet.intersection(OrderedSet([0, 1, 2, 3]), [1, 2, 3])
>>> print(oset)
OrderedSet([1, 2, 3])
>>> oset.intersection([2, 4, 5], [1, 2, 3, 4])
OrderedSet([2])
>>> oset.intersection()
OrderedSet([1, 2, 3])
```

### Difference

```python
>>> OrderedSet([1, 2, 3]).difference(OrderedSet([2]))
OrderedSet([1, 3])
>>> OrderedSet([1, 2, 3]).difference(OrderedSet([2]), OrderedSet([3]))
OrderedSet([1])
>>> OrderedSet([1, 2, 3]) - OrderedSet([2])
OrderedSet([1, 3])
>>> OrderedSet([1, 2, 3]).difference()
OrderedSet([1, 2, 3])
```

### Subset Testing

```python
>>> OrderedSet([1, 2, 3]).issubset({1, 2})
False
>>> OrderedSet([1, 2, 3]).issubset({1, 2, 3, 4})
True
>>> OrderedSet([1, 2, 3]).issubset({1, 4, 3, 5})
False
```

### Superset Testing

```python
>>> OrderedSet([1, 2]).issuperset([1, 2, 3])
False
>>> OrderedSet([1, 2, 3, 4]).issuperset({1, 2, 3})
True
>>> OrderedSet([1, 4, 3, 5]).issuperset({1, 2, 3})
False
```

### Symmetric Difference

```python
>>> this = OrderedSet([1, 4, 3, 5, 7])
>>> other = OrderedSet([9, 7, 1, 3, 2])
>>> this.symmetric_difference(other)
OrderedSet([4, 5, 9, 2])
```

## In-Place Set Operations

### Difference Update

```python
>>> this = OrderedSet([1, 2, 3])
>>> this.difference_update(OrderedSet([2, 4]))
>>> print(this)
OrderedSet([1, 3])

>>> this = OrderedSet([1, 2, 3, 4, 5])
>>> this.difference_update(OrderedSet([2, 4]), OrderedSet([1, 4, 6]))
>>> print(this)
OrderedSet([3, 5])
```

### Intersection Update

```python
>>> this = OrderedSet([1, 4, 3, 5, 7])
>>> other = OrderedSet([9, 7, 1, 3, 2])
>>> this.intersection_update(other)
>>> print(this)
OrderedSet([1, 3, 7])
```

### Symmetric Difference Update

```python
>>> this = OrderedSet([1, 4, 3, 5, 7])
>>> other = OrderedSet([9, 7, 1, 3, 2])
>>> this.symmetric_difference_update(other)
>>> print(this)
OrderedSet([4, 5, 9, 2])
```
