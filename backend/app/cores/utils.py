from pathlib import Path
import hashlib


def as_posix(*paths: str) -> str:
    return Path().joinpath(*paths).as_posix()


def gen_id(src: str, len: int = 12) -> int:
    hash_id = str(int(hashlib.md5(src.encode()).hexdigest(), 16))
    try:
        lim_id = int(hash_id[:len])
    except:
        lim_id = int(hash_id)
    return lim_id
