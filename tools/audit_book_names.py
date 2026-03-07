import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenamePlan:
    source: Path
    destination: Path


@dataclass(frozen=True)
class Collision:
    parent: Path
    normalized_name: str
    sources: tuple[Path, ...]


@dataclass(frozen=True)
class AuditReport:
    rename_plans: tuple[RenamePlan, ...]
    collisions: tuple[Collision, ...]


def normalize_name(name: str) -> str:
    return name.strip()


def analyze_book_names(books_root: str | Path = "static/books") -> AuditReport:
    root = Path(books_root).resolve()
    if not root.exists():
        raise FileNotFoundError(f"books root does not exist: {root}")

    entries = sorted(
        (path for path in root.rglob("*")),
        key=lambda path: (len(path.relative_to(root).parts), str(path)),
    )

    rename_plans: list[RenamePlan] = []
    collisions: list[Collision] = []
    sibling_map: dict[Path, dict[str, list[Path]]] = {}

    for path in entries:
        parent = path.parent.resolve()
        sibling_map.setdefault(parent, {})
        normalized_name = normalize_name(path.name)
        sibling_map[parent].setdefault(normalized_name, []).append(path.resolve())

        if normalized_name != path.name:
            rename_plans.append(RenamePlan(source=path.resolve(), destination=(path.parent / normalized_name).resolve()))

    for parent, grouped in sibling_map.items():
        for normalized_name, sources in grouped.items():
            if len(sources) > 1:
                collisions.append(
                    Collision(
                        parent=parent,
                        normalized_name=normalized_name,
                        sources=tuple(sorted(sources)),
                    )
                )

    rename_plans.sort(key=lambda plan: len(plan.source.relative_to(root).parts), reverse=True)
    collisions.sort(key=lambda collision: (str(collision.parent), collision.normalized_name))
    return AuditReport(rename_plans=tuple(rename_plans), collisions=tuple(collisions))


def apply_rename_plan(report: AuditReport) -> int:
    if report.collisions:
        raise RuntimeError("cannot apply normalization while name collisions exist")

    renamed = 0
    for plan in report.rename_plans:
        if not plan.source.exists():
            continue
        plan.source.rename(plan.destination)
        renamed += 1
    return renamed


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
