import os


def relative_path_from_file(filename: str, path: str) -> str:
    return os.path.join(os.path.dirname(filename), *path.split("/"))
