# M0 — Repo scaffold & quality gates

| ID | Title | Description | Files | Commands | DoD | Labels | TimeboxMinutes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | Initialize repo & dev tooling | Create Makefile, pyproject.toml, pre-commit, ruff, mypy, pytest, docker-compose.yml. | Makefile; pyproject.toml; .pre-commit-config.yaml; docker-compose.yml | make setup; make lint; make test | All tools run locally; pre-commit hooks active; tests green. | infra,tooling | 90 |
| T-002 | Devcontainer / local env | Add VS Code devcontainer with Python 3.12 and Node 20. | .devcontainer/devcontainer.json; .devcontainer/Dockerfile | (open in VS Code) | Codespace/devcontainer boots; make commands work. | infra,devex | 60 |
| T-003 | CI (GitHub Actions) | Setup CI to run lint, type-check, tests on PR. | .github/workflows/ci.yaml |  | CI passes on PR; required checks enabled. | ci | 60 |
| T-004 | Project configs | Add .env.example with Azure OpenAI, Redis, SQLite; document secrets. | .env.example; README.md |  | Boots locally with copied .env. | docs,infra | 45 |
