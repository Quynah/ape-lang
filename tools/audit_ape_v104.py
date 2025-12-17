from __future__ import annotations

import argparse
import os
import subprocess
import sys
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

IGNORED_DIRS = {
    ".git",
    ".svn",
    ".hg",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}

TEXT_EXTENSIONS = {
    ".py",
    ".ape",
    ".md",
    ".txt",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".rst",
    ".csv",
    ".tsv",
}

SEARCH_TERMS = [
    "record",
    "struct",
    "object",
    "dict",
    "map",
    "filter",
    "reduce",
    "group",
    "group_by",
    "aggregate",
    "datetime",
    "timestamp",
    "iso",
    "timezone",
    "utc",
    "now",
    "parse",
    "json",
    "path",
    "dotted",
    "get(",
    "traverse",
    "payload",
    "serialize",
    "deserialize",
    "to_json",
    "from_json",
    "value",
    "type",
    "list",
    "array",
    "stdlib",
    "builtins",
    "native",
    "intrinsic",
]

COMPONENT_PATTERNS = {
    "parser": ["parser"],
    "lexer": ["lexer", "tokenizer"],
    "ast": ["ast", "ir"],
    "runtime": ["runtime"],
    "builtins": ["builtins", "std", "collections", "math", "strings"],
    "stdlib": ["ape_std", "stdlib", "std"],
}

IMPORTANT_SUBTREES = {
    ".": 1,
    "packages": 1,
    "packages/ape": 2,
    "packages/ape/src": 2,
    "packages/ape/src/ape": 2,
}


@dataclass
class SearchHit:
    term: str
    path: Path
    line_no: int
    snippet: str

    def format(self, root: Path) -> str:
        rel = self.path.relative_to(root)
        snippet = self.snippet.strip().replace("\t", " ")
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        return f"- {rel}:{self.line_no}: {snippet}"


def discover_root(script_path: Path) -> Path:
    return script_path.resolve().parents[1]


def iter_text_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        current = Path(dirpath)
        if any(parent.name in IGNORED_DIRS for parent in current.parents):
            continue
        for filename in filenames:
            path = current / filename
            if path.suffix.lower() in TEXT_EXTENSIONS or not path.suffix:
                yield path


def build_tree_listing(root: Path, target: Path, max_depth: int) -> list[str]:
    lines: list[str] = []
    base = (root / target).resolve()
    if not base.exists():
        return [f"(missing) {target}"]

    def walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        entries = [p for p in current.iterdir() if p.name not in IGNORED_DIRS]
        entries.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        indent = "  " * depth
        for entry in entries:
            marker = "/" if entry.is_dir() else ""
            rel = entry.relative_to(root)
            lines.append(f"{indent}- {rel}{marker}")
            if entry.is_dir():
                walk(entry, depth + 1)

    header = f"[tree] {target} (depth {max_depth})"
    lines.append(header)
    walk(base, 0)
    lines.append("")
    return lines


def detect_components(root: Path) -> dict[str, list[Path]]:
    hits: dict[str, list[Path]] = {k: [] for k in COMPONENT_PATTERNS}
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        current = Path(dirpath)
        rel = current.relative_to(root)
        rel_str = "/".join(rel.parts)
        lower = rel_str.lower()
        for component, keywords in COMPONENT_PATTERNS.items():
            if any(keyword in lower for keyword in keywords):
                hits[component].append(rel)
    return hits


def scan_terms(root: Path, max_hits: int) -> dict[str, list[SearchHit]]:
    results: dict[str, list[SearchHit]] = defaultdict(list)
    lowered_terms = [term.lower() for term in SEARCH_TERMS]
    term_set = list(zip(SEARCH_TERMS, lowered_terms))

    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="latin-1")
            except Exception:
                continue
        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            lower_line = line.lower()
            for original_term, lowered_term in term_set:
                if lowered_term in lower_line:
                    if len(results[original_term]) >= max_hits:
                        continue
                    results[original_term].append(
                        SearchHit(
                            term=original_term,
                            path=path,
                            line_no=idx,
                            snippet=line.strip(),
                        )
                    )
    return results


def run_cli_probe(command: list[str], env: dict[str, str], cwd: Path) -> tuple[int, str, str]:
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        cwd=str(cwd),
        env=env,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def run_probes(root: Path, probe_dir: Path) -> list[str]:
    logs: list[str] = []
    if not probe_dir.exists():
        logs.append(f"(no probes found at {probe_dir})")
        return logs

    env = os.environ.copy()
    packages_path = root / "packages"
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{packages_path}{os.pathsep}{existing}" if existing else str(packages_path)

    help_cmd = [sys.executable, "-m", "ape.cli", "parse", "--help"]
    logs.append("[cli] python -m ape.cli parse --help")
    code, out, err = run_cli_probe(help_cmd, env, root)
    logs.append(f"  exit={code}")
    if out:
        logs.append(textwrap.indent(out, prefix="    OUT: "))
    if err:
        logs.append(textwrap.indent(err, prefix="    ERR: "))
    if code != 0:
        logs.append("  CLI help failed; skipping probe execution.")
        return logs

    ape_files = sorted(probe_dir.glob("*.ape"))
    if not ape_files:
        logs.append(f"(probe dir {probe_dir} has no .ape files)")
        return logs

    for ape_file in ape_files:
        cmd = [sys.executable, "-m", "ape.cli", "validate", str(ape_file)]
        logs.append(f"[probe] {' '.join(cmd)}")
        code, out, err = run_cli_probe(cmd, env, root)
        logs.append(f"  exit={code}")
        if out:
            logs.append(textwrap.indent(out, prefix="    OUT: "))
        if err:
            logs.append(textwrap.indent(err, prefix="    ERR: "))
    return logs


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="APE v1.0.4 audit helper")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Path to the Ape repository root (defaults to tools/..)",
    )
    parser.add_argument(
        "--probe-dir",
        type=Path,
        default=None,
        help="Directory containing .ape probe scripts (defaults to <root>/probes)",
    )
    parser.add_argument(
        "--max-search-results",
        type=int,
        default=25,
        help="Maximum hits to record per search term",
    )
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    script_path = Path(__file__)
    root = Path(args.root).resolve() if args.root else discover_root(script_path)
    probe_dir = Path(args.probe_dir).resolve() if args.probe_dir else root / "probes"

    print(f"[root] {root}")
    print(f"[probe_dir] {probe_dir}")

    print("\n=== Repository Tree Overview ===")
    for rel, depth in IMPORTANT_SUBTREES.items():
        rel_display = rel if rel != "." else "root"
        lines = build_tree_listing(root, Path(rel) if rel != "." else Path("."), depth)
        print(f"-- {rel_display} --")
        for line in lines:
            print(line)

    print("\n=== Component Detection ===")
    components = detect_components(root)
    for name, paths in components.items():
        if paths:
            print(f"{name}: {len(paths)} hit(s)")
            for rel in sorted({str(p) for p in paths})[:10]:
                print(f"  - {rel}")
        else:
            print(f"{name}: (no matches)")

    print("\n=== Full-text Search Results ===")
    search_results = scan_terms(root, args.max_search_results)
    for term in SEARCH_TERMS:
        hits = search_results.get(term, [])
        print(f"[{term}] {len(hits)} match(es)")
        if not hits:
            continue
        for hit in hits:
            print(hit.format(root))
        print("")

    print("=== CLI / Probe Checks ===")
    for line in run_probes(root, probe_dir):
        print(line)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
