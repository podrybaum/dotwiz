from typing import TypeVar, Mapping, Callable

_T = TypeVar('_T')
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')

_GetAttr = Callable[[dict, str], _VT]
_GetItem = Callable[[dict, _KT], _VT]
_SetItem = Callable[[dict, _KT, _VT], None]
_Update = Callable[[dict, Mapping[_KT, _VT], _VT], None]


def make_dot_wiz(input_dict: Mapping[_KT, _VT] | None = None,
                 **kwargs: _VT) -> DotWiz: ...

def __dot_wiz_from_dict__(input_dict: Mapping[_KT, _VT]) -> DotWiz: ...

def __setitem_impl__(self: DotWiz, key: _KT, value: _VT, __set: _SetItem = dict.__setitem__): ...

def __resolve_value__(value: _T) -> _T | DotWiz | list[DotWiz]: ...


class DotWiz(dict):

    @classmethod
    def from_dict(cls, input_dict: Mapping[_KT, _VT]) -> DotWiz: ...

    @classmethod
    def from_kwargs(cls, input_dict: Mapping[_KT, _VT] | None = None,
                    **kwargs: _VT) -> DotWiz: ...

    def __delattr__(self, item: str) -> None: ...
    def __delitem__(self, v: _KT) -> None: ...

    def __getattr__(self, item: str) -> _VT: ...
    def __getitem__(self, k: _KT) -> _VT: ...

    def __setattr__(self, item: str, value: _VT) -> None: ...
    def __setitem__(self, k: _KT, v: _VT) -> None: ...

    def __getattribute__(self,
                         key: str,
                         __attr: _GetAttr = dict.__getattribute__,
                         __item: _GetItem = dict.__getitem__): ...

    def update(self,
               __m: Mapping[_KT, _VT],
               __update: _Update = dict.update,
               **kwargs: _T) -> None: ...

    def __repr__(self) -> str: ...
