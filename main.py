"""DotWiz - forked from https://github.com/rnag/dotwiz."""

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
    """Create and return a `DotWiz` from a dict and optional keyword arguments."""
    kwargs.update(*args)
    return DotWiz(kwargs)


def _resolve_value(value, preprocess=True):
    """Resolve value while iterating over a data structure during conversion processes."""
    if not preprocess or not isinstance(
        value, (list, dict)
    ):  # 3.0 for original, 6.9 total for both, this is 4.8
        return value
    try:
        if preprocess and "append" in value.__class__.__dict__:
            return [_resolve_value(e, preprocess) for e in value]
        if "fromkeys" in value.__class__.__dict__:
            return DotWiz(value, preprocess)
    except AttributeError:
        pass
    return value


def _upsert_into_dot_wiz(
    self,
    input_dict: Optional[dict] = None,
    preprocess: Optional[bool] = False,
    **kwargs,
) -> "DotWiz":
    """Create or update a `DotWiz` from a dict and optional keyword arguments.

    Args:
    ----
        self (`DotWiz`): DotWiz instance.
        input_dict (Optional[dict]): Input dict.
        preprocess (Optional[bool]): Whether to convert internal dictionary objects at instantion or
        not.
        kwargs: Optional keyword arguments.

    """
    if not kwargs and not input_dict:
        return

    combined_dict = {**input_dict, **kwargs} if input_dict else kwargs
    if not preprocess:
        self.__dict__.update(combined_dict)
        return

    for key in combined_dict:
        if "fromkeys" in combined_dict[key].__class__.__dict__:
            self.__dict__[key] = DotWiz(
                combined_dict[key], preprocess
            )
            continue
        if "append" in combined_dict[key].__class__.__dict__:
            self.__dict__[key] = [_resolve_value(e) for e in combined_dict[key]]
            continue
        self.__dict__[key] = combined_dict[key]


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
                k: _resolve_value(other[k], check_lists) for k in other
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
            k: _resolve_value(other[k], check_lists) for k in other
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

    #print_char = "☣"

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

    def _setitem_impl(self, key: Any, value: Any, preprocess: bool = True) -> None:
        """Implement `DotWiz.__setitem__` to preserve dot access."""
        if key in ("__dict__", "preprocess"):
            super().__setattr__(key, value)
        else:
            self.__dict__[key] = _resolve_value(value, preprocess)

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

    def __getitem__(self, key, __default=None) -> Any:
        """Implement `__getitem__` with default dict behavior."""
        try:
            return self.get(key)
        except TypeError:
            return self.__dict__[key]

    def __getattr__(self, item: str, __default=None) -> Any:
        """Implement `__getattr__` with default dict behavior."""
        if item in self.__dict__:
            value = self.__dict__[item]
            if isinstance(value, dict) and not self.preprocess:
                value = DotWiz(value)
                self.__dict__[item] = value
            return value
        self.__dict__[item] = __default
        return __default

    def __getattribute__(self, name):
        """Override getattribute to implement preprocessing logic."""
        if name in (
            "preprocess",
            "__dict__",
            "__class__",
            "__slots__",
            "_upsert_into_dot_wiz",
            "_resolve_value",
        ):
            return super().__getattribute__(name)
        try:
            value = super().__getattribute__("__dict__")[name]
            if isinstance(value, dict) and not super().__getattribute__("preprocess"):
                value = DotWiz(value)
                super().__getattribute__("__dict__")[name] = value
            return value
        except KeyError:
            return super().__getattribute__(name)

    __setattr__ = __setitem__ = _setitem_impl

    def __iter__(self) -> Generator:
        """Implement `__iter__`."""
        return iter(self.__dict__.items())

    def __len__(self) -> int:
        """Implement `__len__`."""
        return len(self.__dict__)

    def __repr__(self) -> str:
        """Implement `__repr__`."""
        return f'({", ".join(f"{k}={v!r}" for k, v in self)})'

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

        self.__dict__[k] = default = _resolve_value(k, check_lists)

        return default
    def __iter__(self):
        keys = [attr for attr in self.__dict__.keys() if not attr.startswith('_')]
        yield from [self.__dict__[key] for key in keys]
    
    def values(self) -> list:
        """Implement `values`."""
        return self.__dict__.values()

    @classmethod
    def from_json(
        cls,
        jsons: Optional[str] = None,
        file: Optional[IO] = None,
        multiline: bool = False,
        **kwargs,
    ) -> "DotWiz":
        """De-serialize a JSON string (or file) as a `DotWiz` instance.

        Args:
        ----
            jsons (Optional[str]): A JSON string to de-serialize.
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

        if not jsons and not file:
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

        return json.loads(jsons, object_hook=__object_hook, **kwargs)

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
        o: "DotWiz",
        file: Optional[str] = None,
        keep_snakes: Optional[bool] = True,
        **kwargs,
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
