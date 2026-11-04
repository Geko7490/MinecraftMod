"""Build every checked-in example, including its version in the asset name."""
from pathlib import Path
import tomllib
from build_hmod import build

ROOT = Path(__file__).resolve().parents[1]

if __name__ == '__main__':
    for source in sorted((ROOT / 'examples').iterdir()):
        manifest = source / 'horizon-mod.toml'
        if manifest.is_file():
            info = tomllib.loads(manifest.read_text(encoding='utf-8'))
            build(source, ROOT / 'target/horizon-mod' / f"{info['id']}-{info['version']}.hmod")
