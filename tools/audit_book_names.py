import argparse
from pathlib import Path

from services.book_names import (
    AuditReport,
    analyze_book_names,
    apply_rename_plan,
    normalize_name,
)


def format_report(report: AuditReport, root: Path) -> str:
    lines: list[str] = []
    lines.append(f"Books root: {root}")
    lines.append(f"Planned renames: {len(report.rename_plans)}")
    lines.append(f"Collisions: {len(report.collisions)}")

    if report.rename_plans:
        lines.append("")
        lines.append("Rename plan:")
        for plan in report.rename_plans:
            lines.append(f"- {plan.source.relative_to(root)} -> {plan.destination.relative_to(root)}")

    if report.collisions:
        lines.append("")
        lines.append("Collisions:")
        for collision in report.collisions:
            joined = ", ".join(str(path.relative_to(root)) for path in collision.sources)
            lines.append(f"- {collision.parent.relative_to(root)} :: {collision.normalized_name} :: {joined}")

    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dry-run audit and optional normalization for book names.")
    parser.add_argument(
        "--books-root",
        default="static/books",
        help="Books root directory to audit (default: static/books)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the planned renames if no collisions are detected",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.books_root).resolve()
    report = analyze_book_names(root)
    print(format_report(report, root))

    if args.apply:
        renamed = apply_rename_plan(report)
        print(f"\nApplied renames: {renamed}")

    return 0 if not report.collisions else 1


if __name__ == "__main__":
    raise SystemExit(main())
