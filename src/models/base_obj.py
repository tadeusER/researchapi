from typing import Any, Dict


class BaseObject:
    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]):
        return cls(**data_dict)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"
