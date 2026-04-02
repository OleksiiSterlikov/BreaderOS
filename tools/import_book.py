import argparse
import shutil
from pathlib import Path

from services.book_names import normalize_book_names, normalize_name


def validate_relative_subdir(value: str | None) -> Path:
    if not value:
        return Path()

    path = Path(value)
    if path.is_absolute():
        raise ValueError("target subdir must be a safe relative path")

    normalized_parts: list[str] = []
    for part in path.parts:
        normalized_part = normalize_name(part)
        if normalized_part in {"", "."}:
            raise ValueError("target subdir must not contain empty path segments")
        if normalized_part == "..":
            raise ValueError("target subdir must be a safe relative path")
        normalized_parts.append(normalized_part)

    return Path(*normalized_parts)


def import_book(
    source: str | Path,
    books_root: str | Path = "static/books",
    target_subdir: str | None = None,
    replace: bool = False,
) -> Path:
    source_path = Path(source).resolve()
    books_root_path = Path(books_root).resolve()
    relative_subdir = validate_relative_subdir(target_subdir)

    if not source_path.exists() or not source_path.is_dir():
        raise FileNotFoundError(f"source directory does not exist: {source_path}")

    normalized_source_name = normalize_name(source_path.name)
    if not normalized_source_name:
        raise ValueError("source directory name becomes empty after normalization")

    destination_parent = books_root_path / relative_subdir
    destination_parent.mkdir(parents=True, exist_ok=True)
    destination = destination_parent / normalized_source_name

    if destination.exists():
        if not replace:
            raise FileExistsError(f"destination already exists: {destination}")
        shutil.rmtree(destination)

    shutil.copytree(source_path, destination)
    normalization_result = normalize_book_names(destination)

    if normalization_result.report.collisions:
        shutil.rmtree(destination)
        raise RuntimeError("imported book contains name collisions after normalization")

    return destination


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import a book directory into static/books.")
    parser.add_argument("source", help="Path to the source book directory")
    parser.add_argument(
        "--books-root",
        default="static/books",
        help="Destination books root directory (default: static/books)",
    )
    parser.add_argument(
        "--target-subdir",
        default=None,
        help="Optional relative subdirectory inside books root",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace destination if it already exists",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    destination = import_book(
        source=args.source,
        books_root=args.books_root,
        target_subdir=args.target_subdir,
        replace=args.replace,
    )
    print(f"Imported book to: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
