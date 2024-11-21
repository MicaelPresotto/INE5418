from dataclasses import dataclass

@dataclass
class Item:
    id: int
    name: str
    value: int
    version: int