from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def contains_all(text: str, patterns: list[str]) -> bool:
    return all(pattern in text for pattern in patterns)


def run_checks() -> list[str]:
    errors: list[str] = []

    app_py = read_text("app.py")
    dockerfile = read_text("Dockerfile")
    compose = read_text("docker-compose.yml")
    routes = read_text("routes/main.py")

    readme = read_text("README.md")
    architecture = read_text("docs/ai/ARCHITECTURE.md")
    development = read_text("docs/ai/DEVELOPMENT.md")
    deployment = read_text("docs/ai/DEPLOYMENT.md")
    security = read_text("docs/ai/SECURITY.md")

    if "def create_app()" in app_py:
        if not contains_all(development, ["create_app()", "APP_DEBUG", "APP_USE_RELOADER"]):
            errors.append("DEVELOPMENT.md does not document the current create_app/env-based local startup flow.")
        if "create_app()" not in readme:
            errors.append("README.md does not mention the create_app()-based entrypoint.")

    if "gunicorn" in dockerfile:
        for doc_name, doc_text in {
            "README.md": readme,
            "ARCHITECTURE.md": architecture,
            "DEPLOYMENT.md": deployment,
        }.items():
            if "Gunicorn" not in doc_text and "gunicorn" not in doc_text:
                errors.append(f"{doc_name} does not mention Gunicorn even though Dockerfile uses it.")

    if "nginx:" in compose and "80:80" in compose:
        for doc_name, doc_text in {
            "README.md": readme,
            "ARCHITECTURE.md": architecture,
            "DEPLOYMENT.md": deployment,
            "SECURITY.md": security,
        }.items():
            if "Nginx" not in doc_text and "nginx" not in doc_text:
                errors.append(f"{doc_name} does not mention Nginx even though docker-compose exposes it.")

    if "resolve_books_path" in routes:
        if "path traversal" not in security:
            errors.append("SECURITY.md does not mention path traversal protection for book routes.")
        if "безпеч" not in architecture.lower() and "безпеч" not in development.lower():
            errors.append("Documentation does not describe safe book route handling.")

    if "/opt/breaderos/static/books" in compose:
        for doc_name, doc_text in {
            "README.md": readme,
            "ARCHITECTURE.md": architecture,
            "DEPLOYMENT.md": deployment,
            "SECURITY.md": security,
        }.items():
            if "/opt/breaderos/static/books" not in doc_text:
                errors.append(f"{doc_name} does not mention the current container books path /opt/breaderos/static/books.")

    if "BOOKS_HOST_PATH" in compose:
        for doc_name, doc_text in {
            "README.md": readme,
            "DEPLOYMENT.md": deployment,
            "DEVELOPMENT.md": development,
        }.items():
            if "BOOKS_HOST_PATH" not in doc_text:
                errors.append(f"{doc_name} does not mention BOOKS_HOST_PATH even though docker-compose uses it.")

    if "http://127.0.0.1" not in readme or "http://127.0.0.1:5000" not in readme:
        errors.append("README.md must describe both compose and direct local addresses.")

    return errors


def main() -> int:
    errors = run_checks()
    if errors:
        print("Documentation consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation consistency check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
