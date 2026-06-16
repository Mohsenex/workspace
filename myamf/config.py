"""Store path."""

__all__ = ["PATH"]

import pathlib

cwd = pathlib.Path.cwd()
module = pathlib.Path(__file__).parent.absolute()
repo = module.parent.parent


class Path:
    module = module
    repo = repo
    gds = module / "gds"


PATH = Path()
