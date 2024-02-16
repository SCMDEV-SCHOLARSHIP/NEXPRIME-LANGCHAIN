from enum import Enum


# constant example: str values
class Constant(str, Enum):
    def __str__(self) -> str:
        return str(self.value)

    BACKEND = "backend"


# use: print(Constant.BACKEND)
# >> backend
