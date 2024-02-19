from pathlib import Path


def as_posix(*paths: str) -> str:
    return Path().joinpath(*paths).as_posix()
