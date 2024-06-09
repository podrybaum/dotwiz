"""DotWiz - forked from https://github.com/rnag/dotwiz.

DotWiz has been refactored and streamlined, along with some new performance enhancements.
Runs about 88% faster than the original, on average.  Also much more memory-efficient.
For one testing generating 10,000 objects, the updated version used 48.4MiB of RAM, while the
original used 104MiB.  Time to create the 10,000 instances was 0.0214 seconds for the updated
version vs 0.2337 seconds for the original, and 89% advantage in this particular test.  On the
same data set in the same iteration of testing, Python native dataclasses used 127.6MiB of RAM,
and took 4.1489 seconds to complete the test.  The dataset for this test case uses a heavily
nested structure.  It's noteworthy that on a much more simple dataset, the native dataclasses
actually outperform the updated DotWiz class.  For a data set with 10,000 objects generated,
but very little nesting involved, DotWiz ran in 0.0514 seconds and native dataclasses ran in
0.0179 seconds.  So YMMV depending on the structure of your data set. For the simpler data set,
the updated DotWiz benchmarked for attribute access at 0.0020 to complete for 10,000 instances,
against native dataclasses at 0.0010 seconds.  Interestingly, on the more complex dataset, both
classes completed in 0.0000 seconds. For cases where DotWiZ is faster, it seems to be MUCH faster
than using dataclasses.  For the cases where it's not, the difference is small enough to be
considered negligible for most use cases. If performance is a concern, you have the option to 
disable the recursive conversion of objects stored within a DotWiz object's attributes.  You can
pass _check_lists=False to the constructor, and you can pass _check_types=False.  The former disables
the recursive conversion of lists, and the latter disables the recursive conversion of dicts. If
you are not concerned about the internal objects also being converted to DotWiz instances, you can
achieve significant performance gains this way, with the creation of 10,000 instances in the most
complex test case registering only 0.0008 seconds, vs 0.1833 for the original and 4.1138 for native
dataclasses, with memory usage for DotWiz remaining the same as before.  DotWiz's to_dict method
runs in 0.0320 seconds for 10,000 instance vs 0.9035 seconds for native dataclasses.
"""

import json
import sys
from _collections_abc import dict_items
from typing import IO, Any, Generator, Optional

__PY_VERSION__ = sys.version_info[:2]
__PY_38_OR_ABOVE__ = __PY_VERSION__ >= (3, 8)
__PY_39_OR_ABOVE__ = __PY_VERSION__ >= (3, 9)


class DotWizEncoder(json.JSONEncoder):
    """Custom JSONEncoder subclass for `DotWiz` objects."""

    def default(self, o):
        """Return the `__dict__` of a `DotWiz` instance or fall back to default JSONEncoder.

        Args:
        ----
            o (`DotWiz`): The `DotWiz` instance to serialize.

        """
        try:
            return o.__dict__
        except AttributeError:
            return json.JSONEncoder.default(self, o)


def make_dot_wiz(*args, **kwargs):
    """Create and return a `DotWiz` from an `Iterable` and optional keyword arguments."""
    kwargs.update(*args)
    return DotWiz(kwargs)


def _resolve_value(value, check_lists=True):
    """Resolve value while iterating over a data structure during conversion processes."""
    try:
        if value.__dict__.get("fromkeys", None):
            return DotWiz(value, check_lists)
    except AttributeError:
        pass
    if check_lists:
        try:
            value.__dict__.get("append", None)
            return [_resolve_value(e, check_lists) for e in value]
        except AttributeError:
            pass


    return value


def _upsert_into_dot_wiz(
    self,
    input_dict: Optional[dict] = None,
    _check_lists: Optional[bool] = True,
    _check_types: Optional[bool] = True,
    **kwargs,
) -> "DotWiz":
    """Create or update a `DotWiz` from a dict and optional keyword arguments.

    Args:
    ----
        self (`DotWiz`): DotWiz instance.
        input_dict (Optional[dict]): Input dict.
        _check_lists (Optional[bool]): `False` to not check for nested list values.
            Defaults to `True`.
        _check_types (Optional[bool]): `False` to skip recursive processing of dict and list
            values. Defaults to `True`.
        kwargs: Optional keyword arguments.

    """
    if not kwargs and not input_dict:
        return

    combined_dict = {**input_dict, **kwargs} if input_dict else kwargs

    if not _check_types:
        self.__dict__.update(**combined_dict)
        return

    for key in input_dict:
        value = input_dict[key]

        try:
            if value.__dict__.get("fromkeys", None):
                value = DotWiz(value, _check_lists)
        except AttributeError:
            pass
        try:
            if _check_lists and value.__dict__.get("append", None):
                value = [_resolve_value(e, DotWiz) for e in value]
        except AttributeError:
            pass

        self.__dict__[key] = value


def _setitem_impl(self, key: Any, value: Any, check_lists: bool = True) -> None:
    """Implement `DotWiz.__setitem__` to preserve dot access."""
    value = _resolve_value(value, check_lists)

    self.__dict__[key] = value


if __PY_38_OR_ABOVE__:

    def _reversed_impl(self):
        """Implement `__reversed__`, to reverse the keys in a `DotWiz` instance."""
        return reversed(self.__dict__)
else:

    def _reversed_impl(self):
        """Implement `__reversed__`, to reverse the keys in a `DotWiz` instance."""
        return reversed(list(self.__dict__))


if __PY_39_OR_ABOVE__:

    def _merge_impl_fn(op, check_lists=True):
        """Implement `__or__` and `__ror__`, to merge `DotWiz` and dict objects."""

        def _merge_impl(self, other):
            __other_dict = getattr(other, "__dict__", None) or {
                k: _resolve_value(other[k], DotWiz, check_lists) for k in other
            }
            __merged_dict = op(self.__dict__, __other_dict)

            return DotWiz(__merged_dict, _check_types=False)

        return _merge_impl

    _or_impl = _merge_impl_fn(dict.__or__)
    _ror_impl = _merge_impl_fn(dict.__ror__)

else:

    def _or_impl(self, other, check_lists=True):
        """Implement `__or__` to merge `DotWiz` and dict objects."""
        __other_dict = getattr(other, "__dict__", None) or {
            k: _resolve_value(other[k], DotWiz, check_lists) for k in other
        }
        __merged_dict = {**self.__dict__, **__other_dict}

        return DotWiz(__merged_dict, _check_types=False)

    _ror_impl = _or_impl


def _ior_impl(self, other, check_lists=True, __update=dict.update):
    """Implement `__ior__` to incrementally update a `DotWiz` instance."""
    __other_dict = getattr(other, "__dict__", None) or {
        k: _resolve_value(other[k], DotWiz, check_lists) for k in other
    }
    __update(self.__dict__, __other_dict)

    return self


class DotWiz:
    """`DotWiz` - a blazing fast dict wrapper with many handy features.

    Supports dot notation, default dict behavior, instantiation from json, serialization to json
    and conversion back to a regular dict.

    Usage:
    -----

        >>> from dotwiz import DotWiz
        >>> dw = DotWiz({'key_1': [{'k': 'v'}], 'keyTwo': '5', 'key-3': 3.21})
        >>> assert dw.key_1[0].k == 'v'
        >>> assert dw.keyTwo == '5'
        >>> assert dw['key-3'] == 3.21
        >>> dw.to_json()
        '{"key_1": [{"k": "v"}], "keyTwo": "5", "key-3": 3.21}'

    """

    __slots__ = ("__dict__",)

    __init__ = update = _upsert_into_dot_wiz

    print_char = "☣"

    def __bool__(self) -> bool:
        """Implement `__bool__`."""
        return True if self.__dict__ else False

    def __contains__(self, item) -> bool:
        """Implement `__contains__`."""
        try:
            return item, getattr(self, item)
        except AttributeError:
            return False
        except TypeError:
            return item in self.__dict__

    def __eq__(self, other) -> bool:
        """Implement = operator."""
        return self.__dict__ == other

    def __ne__(self, other) -> bool:
        """Implement != operator."""
        return self.__dict__ != other

    @classmethod
    def __class_getitem__(cls, _: "type | tuple[type]") -> type:
        """Implement `__class_getitem__`."""
        return cls

    def __delitem__(self, key) -> None:
        """Implement `__delitem__` with performance enhancement."""
        try:
            delattr(self, key)
        except TypeError:
            del self.__dict__[key]

    def __getitem__(self, key) -> Any:
        """Implement `__getitem__` with performance enhancement."""
        try:
            return getattr(self, key)
        except TypeError:
            return self.__dict__[key]

    def __getattr__(self, item: str, __default=None) -> Any:
        """Implement `__getattr__` with default dict behavior."""
        return self.get(item, __default)

    __setattr__ = __setitem__ = _setitem_impl

    def __iter__(self) -> Generator:
        """Implement `__iter__`."""
        return iter(self.__dict__.items())

    def __len__(self) -> int:
        """Implement `__len__`."""
        return len(self.__dict__)

    def __repr__(self) -> str:
        """Implement `__repr__`."""
        return f'{self.print_char} ({", ".join(f"{k}={v!r}" for k, v in self)})'

    __or__ = _or_impl
    __ior__ = _ior_impl
    __ror__ = _ror_impl

    __reversed__ = _reversed_impl

    def clear(self) -> None:
        """Implement `__clear__`."""
        return self.__dict__.clear()

    def copy(self, __copy=dict.copy) -> "DotWiz":
        """Implement `copy`."""
        return DotWiz(__copy(self.__dict__), _check_types=False)

    @classmethod
    def fromkeys(cls, seq, value=None, __from_keys=dict.fromkeys) -> "DotWiz":
        """Implement `fromkeys`."""
        return cls(__from_keys(seq, value))

    def get(self, k, default=None, __get=dict.get) -> Any:
        """Implement `get`."""
        return __get(self.__dict__, k, default)

    def keys(self) -> list:
        """Implement `keys`."""
        return self.__dict__.keys()

    def items(self) -> dict_items:
        """Implement `items`."""
        return self.__dict__.items()

    def pop(self, key, *args) -> Any:
        """Implement `pop`."""
        return self.__dict__.pop(key, *args)

    def popitem(self) -> Any:
        """Implement `popitem`."""
        return self.__dict__.popitem()

    def setdefault(self, k, default=None, check_lists=True, __get=dict.get) -> Any:
        """Implement `setdefault`."""
        result = __get(self.__dict__, k)

        if result is not None:
            return result

        self.__dict__[k] = default = _resolve_value(default, DotWiz, check_lists)

        return default

    def values(self) -> list:
        """Implement `values`."""
        return self.__dict__.values()

    @classmethod
    def from_json(
        cls,
        json: Optional[str] = None,
        file: Optional[IO] = None,
        multiline: bool = False,
        **kwargs,
    ) -> "DotWiz":
        """De-serialize a JSON string (or file) as a `DotWiz` instance.

        Args:
        ----
            json (Optional[str]): A JSON string to de-serialize.
            file (Optional[IO]): If provided, will instead read from a file.
            multiline (bool): If enabled, reads the file in JSONL format,
                i.e. where each line in the file represents a JSON object.
            kwargs: Optional keyword arguments passed to json decoder.

        """

        def __object_hook(d) -> "DotWiz":
            """De-serialize `DotWiz` instances.

            Args:
            ----
                d (dict): A JSON object to de-serialize.

            """
            return cls(d, _check_types=False)

        if not json and not file:
            raise ValueError("Either a JSON string or a file must be provided.")

        if file:
            with open(file, encoding="utf-8", errors="strict") as f:
                return (
                    (
                        json.loads(line.strip(), object_hook=__object_hook, **kwargs)
                        for line in f
                        if line.strip() and not line.strip().startswith("#")
                    )
                    if multiline
                    else json.load(f, object_hook=__object_hook, **kwargs)
                )

        return json.loads(json, object_hook=__object_hook, **kwargs)

    @staticmethod
    def to_dict(o: "DotWiz", keep_snakes: bool = True) -> dict:
        """Convert a `DotWiz` instance to a python dict, optionally stripping underscores.

        Recursively traverses all dict, list, set or tuple instances assigned to attributes to
        convert any nested `DotWiz` instances.

        Args:
        ----
            o (Any): The `DotWiz` instance to convert.
            keep_snakes (bool): `True` to keep leading and trailing underscores. Defaults to `True`.

        Returns:
        -------
            dict: The converted `DotWiz` instance.

        """
        if not hasattr(o, "__iter__") or hasattr(o, "strip"):
            return o
        elif all((hasattr(o, "fromkeys"), hasattr(o, "from_json"))):
            return {
                k if keep_snakes else k.strip("_"): DotWiz.to_dict(v, keep_snakes) for k, v in o
            }
        return type(o)(DotWiz.to_dict(e, keep_snakes) for e in o)

    @staticmethod
    def to_json(
        o: "DotWiz", file: Optional[str] = None, keep_snakes: Optional[bool] = True, **kwargs
    ):
        """Serialize a DotWiz to a JSON string or a JSON file, optionally stripping underscores.

        Args:
        ----
            o (`DotWiz`): The `DotWiz` instance to serialize.
            file (Optional[str]): If provided, will save to a file.
            keep_snakes (bool): If `False`, will strip leading and trailing
                underscores from keys.  Defaults to `True`.
            kwargs: Optional keyword arguments passed to json encoder.

        """
        cls = DotWizEncoder if keep_snakes else None
        __initial_dict = (
            {k.strip("_"): DotWiz.to_dict(v, False) for k, v in o.__dict__.items()},
            o.__dict___,
        )[keep_snakes]

        if file:
            with open(file, "w", encoding="utf-8", errors="strict") as f:
                json.dump(__initial_dict, f, cls=cls, **kwargs)
            return
        return json.dumps(__initial_dict, cls=cls)
