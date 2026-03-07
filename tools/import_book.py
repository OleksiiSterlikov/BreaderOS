import argparse
import shutil
from pathlib import Path


def validate_relative_subdir(value: str | None) -> Path:
    if not value:
        return Path()

    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("target subdir must be a safe relative path")

    return path


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

    destination_parent = books_root_path / relative_subdir
    destination_parent.mkdir(parents=True, exist_ok=True)
    destination = destination_parent / source_path.name

    if destination.exists():
        if not replace:
            raise FileExistsError(f"destination already exists: {destination}")
        shutil.rmtree(destination)

    shutil.copytree(source_path, destination)
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
