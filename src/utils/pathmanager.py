from pathlib import Path

class PathNotFound(Exception):

    def __init__(self, pathname: str, path: Path):
        msg = f'path {pathname} not found at {path}'
        super().__init__(msg)

class PathManager:
    def __init__(self, project_root: Path | None = None):
        self.project = Path(__file__).parents[2] if project_root is None else project_root
        self.src     = self.project / 'src'
        self.data    = self.project / 'data'

        self._assert_path_integrity()

    def _assert_path_integrity(self):
        path: Path 
        for pathname, path in vars(self).items():
            if not path.exists() and pathname != 'history':
                raise PathNotFound(pathname, path)
