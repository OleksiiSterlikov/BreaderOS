import logging
import time
from dataclasses import dataclass
from pathlib import Path
from threading import Lock


logger = logging.getLogger(__name__)


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


@dataclass(frozen=True)
class NormalizationResult:
    report: AuditReport
    renamed: int


_AUTO_NORMALIZE_INTERVAL_SECONDS = 1.0
_auto_normalize_lock = Lock()
_last_auto_normalize_at: dict[str, float] = {}
_last_collision_signatures: dict[str, tuple[tuple[str, str, tuple[str, ...]], ...]] = {}


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
            rename_plans.append(
                RenamePlan(
                    source=path.resolve(),
                    destination=(path.parent / normalized_name).resolve(),
                )
            )

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


def normalize_book_names(books_root: str | Path = "static/books") -> NormalizationResult:
    report = analyze_book_names(books_root)
    renamed = 0

    if report.rename_plans and not report.collisions:
        renamed = apply_rename_plan(report)

    return NormalizationResult(report=report, renamed=renamed)


def ensure_book_names_normalized(
    books_root: str | Path,
    min_interval_seconds: float = _AUTO_NORMALIZE_INTERVAL_SECONDS,
) -> NormalizationResult | None:
    root = Path(books_root).resolve()
    if not root.exists():
        return None

    root_key = str(root)
    now = time.monotonic()
    last_run_at = _last_auto_normalize_at.get(root_key, 0.0)
    if now - last_run_at < min_interval_seconds:
        return None

    with _auto_normalize_lock:
        last_run_at = _last_auto_normalize_at.get(root_key, 0.0)
        now = time.monotonic()
        if now - last_run_at < min_interval_seconds:
            return None

        result = normalize_book_names(root)
        _last_auto_normalize_at[root_key] = time.monotonic()

        if result.report.collisions:
            collision_signature = tuple(
                (
                    str(collision.parent),
                    collision.normalized_name,
                    tuple(str(path) for path in collision.sources),
                )
                for collision in result.report.collisions
            )
            if _last_collision_signatures.get(root_key) != collision_signature:
                logger.warning(
                    "Skipped automatic book-name normalization under %s because collisions were detected.",
                    root,
                )
                _last_collision_signatures[root_key] = collision_signature
        else:
            _last_collision_signatures.pop(root_key, None)
            if result.renamed:
                logger.info("Normalized %s book paths under %s", result.renamed, root)

        return result
