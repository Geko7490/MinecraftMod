#!/usr/bin/env python3
"""Build a content-only Horizon .hmod package without a private SDK checkout."""
from __future__ import annotations
import argparse
import json
import re
import tomllib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

MAX_BYTES = 64 * 1024 * 1024
ALLOWED_CAPS = {"game-read", "chat", "hud", "storage", "command", "registries", "ui", "render", "input", "players", "world", "recipes"}

def build(source: Path, output: Path) -> Path:
    source = source.resolve()
    manifest_path = source / "horizon-mod.toml"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing {manifest_path}")
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    mod_id, version = manifest.get("id", ""), manifest.get("version", "")
    if not re.fullmatch(r"[a-z0-9_]{1,64}", mod_id):
        raise SystemExit("Manifest id must match [a-z0-9_]{1,64}")
    if not version or manifest.get("api") not in {"0.1", "0.2", "0.3"}:
        raise SystemExit("Manifest needs a version and supported api")
    if manifest.get("side", "client") not in {"client", "server", "both"}:
        raise SystemExit("Manifest side must be client, server or both")
    caps = set(manifest.get("capabilities", []))
    if not caps <= ALLOWED_CAPS:
        raise SystemExit(f"Unknown capabilities: {sorted(caps - ALLOWED_CAPS)}")
    if "registries" not in caps:
        raise SystemExit("A content-only .hmod needs the registries capability")
    files = [manifest_path]
    for folder in ("assets", "data"):
        root = source / folder
        if root.exists():
            for path in sorted(root.rglob("*")):
                if path.is_symlink():
                    raise SystemExit(f"Symlinks are not allowed: {path}")
                if not path.is_file():
                    continue
                rel = path.relative_to(source).as_posix()
                if rel.startswith("/") or ".." in Path(rel).parts or "\\" in rel:
                    raise SystemExit(f"Unsafe package path: {rel}")
                raw = path.read_bytes()
                if path.suffix == ".json":
                    try:
                        json.loads(raw)
                    except Exception as exc:
                        raise SystemExit(f"Invalid JSON {rel}: {exc}") from exc
                if path.suffix == ".png" and not raw.startswith(b"\\x89PNG\\r\\n\\x1a\\n"):
                    raise SystemExit(f"Invalid PNG texture: {rel}")
                files.append(path)
    if len(files) < 2:
        raise SystemExit("A content mod needs assets/ or data/ files")
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(source).as_posix())
    if output.stat().st_size > MAX_BYTES:
        output.unlink(missing_ok=True)
        raise SystemExit("The .hmod exceeds 64 MiB")
    with ZipFile(output) as archive:
        if archive.testzip() is not None or archive.namelist().count("horizon-mod.toml") != 1:
            output.unlink(missing_ok=True)
            raise SystemExit("Generated .hmod failed ZIP validation")
        parsed = tomllib.loads(archive.read("horizon-mod.toml").decode("utf-8"))
        if parsed.get("id") != mod_id or parsed.get("version") != version:
            raise SystemExit("Generated package manifest changed unexpectedly")
    print(f"Built {output} ({output.stat().st_size} bytes)")
    return output

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("examples/ruby-content"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = tomllib.loads((args.source / "horizon-mod.toml").read_text(encoding="utf-8"))
    output = args.output or Path("target/horizon-mod") / f"{manifest['id']}.hmod"
    build(args.source, output)

if __name__ == "__main__":
    main()
