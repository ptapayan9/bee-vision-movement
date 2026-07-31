# bee-vision-movement

Video analysis and movement tracking for studying how bees see the world.

## Local development

### Prerequisites

- [Git](https://git-scm.com/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

Python does not need to be installed separately. The repository's
`.python-version` file tells `uv` to use Python 3.12.

### Set up the project

Clone the repository and enter its directory:

```bash
git clone git@github.com:ptapayan9/bee-vision-movement.git
cd bee-vision-movement
```

Install the required Python version and synchronize the environment from the
committed lockfile:

```bash
uv python install
uv sync --locked
```

`uv` creates a local `.venv` and installs the project in editable mode. Run
commands with `uv run`; activating the virtual environment is optional.

Verify that the package is installed from the `src` directory:

```bash
uv run python -c "import bvm; print(bvm.__file__)"
```

The printed path should end with `src/bvm/__init__.py`.

### Run development checks

Run the same checks locally before opening a pull request:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv build
```

The test command reports that no tests were collected until the first tests are
added under `tests/`.

### Manage dependencies

Use `uv` to keep `pyproject.toml`, `uv.lock`, and the local environment in sync:

```bash
uv add numpy
uv add --dev hypothesis
uv remove numpy
```

Runtime dependencies belong under `[project].dependencies`. Test, lint, and
type-checking tools belong under `[dependency-groups].dev`. Commit
`pyproject.toml`, `uv.lock`, and `.python-version`, but do not commit `.venv`.
