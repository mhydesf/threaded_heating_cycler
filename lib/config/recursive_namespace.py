from types import SimpleNamespace
from typing import Dict, Any, Iterable, Optional, Tuple


class RecursiveNamespace(SimpleNamespace):
    @staticmethod
    def map_entry(entry: Dict[Any, Any]) -> Any:
        if isinstance(entry, dict):
            return RecursiveNamespace(**entry)
        return entry

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.update(kwargs)

    def to_dict(self) -> dict:
        conversion = dict()
        self._to_dict_recurse(conversion)
        return conversion

    def _to_dict_recurse(self, conversion: dict) -> None:
        for attr_name, attr_val in self.__dict__.items():
            if isinstance(attr_val, RecursiveNamespace):
                conversion[attr_name] = attr_val.to_dict()
            elif type(attr_val) == list or type(attr_val) == tuple:
                result = []
                for list_attr in attr_val:
                    if isinstance(list_attr, RecursiveNamespace):
                        result.append(list_attr.to_dict())
                    else:
                        result.append(list_attr)
                conversion[attr_name] = result
            else:
                conversion[attr_name] = attr_val

    def get_nested(self, keys: tuple) -> Any:
        return self._get_nested_recurse(self, list(keys))

    def get_nested_default(
        self,
        keys: tuple,
        default: Optional[Any]=None
    ) -> Any:
        try:
            return self.get_nested(keys)
        except AttributeError:
            return default

    def _get_nested_recurse(
        self,
        tree: Any,
        keys: list
    ) -> Any:
        if len(keys) == 0:
            return tree
        key = keys.pop(0)
        value = tree[key]
        if isinstance(value, RecursiveNamespace) or type(value) == list or type(value) == tuple:
            return self._get_nested_recurse(value, keys)
        else:
            if len(keys) != 0:
                raise AttributeError(
                    "Supplied sub keys are not accounted for: " + str(keys))

            return value

    def set_nested(
        self,
        keys: tuple,
        value: Any,
        create: Optional[bool]=False
    ) -> None:
        if isinstance(value, dict):
            value = RecursiveNamespace(**value)
        self._set_nested_recurse(self, list(keys), value, create)

    def _set_nested_recurse(
        self,
        tree: Any,
        keys: list,
        value: Any,
        create: bool,
    ) -> Any:
        key = keys.pop(0)
        if len(keys) == 0:
            tree[key] = value
            return

        if create and key not in tree.__dict__.keys():
            tree[key] = RecursiveNamespace()
        next_tree = tree[key]
        if isinstance(next_tree, RecursiveNamespace) or type(next_tree) == list or type(next_tree) == tuple:
            return self._set_nested_recurse(next_tree, keys, value, create)
        elif len(keys) != 0:
            raise AttributeError(
                "Supplied sub keys are not accounted for: " + str(keys))

    def get(self, key: Any, default: Any=None) -> Any:
        if key in self.keys():
            return self[key]
        else:
            return default

    def flatten(
        self,
        stringify_separator: Optional[str]=None,
    ) -> dict:
        flat = {}
        self._flatten_recurse([], flat, self.__dict__)
        if stringify_separator is not None:
            assert type(stringify_separator) == str
            stringify_flat = {}
            for key in flat.keys():
                str_key = "/".join(list(map(str, key)))
                stringify_flat[str_key] = flat[key]
            return stringify_flat
        else:
            return flat

    def _flatten_recurse(
        self,
        root_key: Any,
        flat: Iterable[Any],
        tree: dict
    ) -> None:
        for attr_name, attr_val in tree.items():
            flat_key = root_key + [attr_name]
            if isinstance(attr_val, RecursiveNamespace):
                self._flatten_recurse(flat_key, flat, attr_val.__dict__)
            elif type(attr_val) == list or type(attr_val) == tuple:
                for index, list_attr in enumerate(attr_val):
                    list_key = flat_key + [index]
                    if isinstance(list_attr, RecursiveNamespace):
                        self._flatten_recurse(
                            list_key, flat, list_attr.__dict__)
                    else:
                        flat[tuple(list_key)] = list_attr
            else:
                flat[tuple(flat_key)] = attr_val

    def items(self) -> Iterable[Tuple[Any, Any]]:
        return self.__dict__.items()

    def keys(self) -> Iterable[Any]:
        return self.__dict__.keys()

    def values(self) -> Iterable[Any]:
        return self.__dict__.values()

    def update(self, d: dict) -> None:
        for key, val in d.items():
            if isinstance(val, dict):
                setattr(self, key, RecursiveNamespace(**val))
            elif type(val) == list or type(val) == tuple:
                setattr(self, key, list(map(self.map_entry, val)))
            else:
                setattr(self, key, val)

    def merge(self, other) -> None:
        if not isinstance(other, RecursiveNamespace):
            raise AttributeError("Merging object is not RecursiveNamespace: <%s>%s" % (
                type(other), repr(other)))
        for key, value in other.items():
            if key in self.keys() and \
                    isinstance(value, RecursiveNamespace) and \
                    isinstance(self[key], RecursiveNamespace):
                self[key].merge(value)
            else:
                self[key] = value

    def __getitem__(self, key: Any) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> Any:
        if isinstance(value, dict):
            value = self.__class__(**value)
        return setattr(self, key, value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            return self.to_dict() == other
        elif isinstance(other, RecursiveNamespace):
            return self.to_dict() == other.to_dict()
        else:
            return False

