# Installation

These steps assume a clean machine with Python 3.10+ available.

1. Clone the repository.
2. From the project root, run `./scripts/bootstrap.sh` to create a virtualenv,
   upgrade `pip`, and install the package in editable mode (including dev
   tooling such as pytest).
3. Activate the environment for the current shell session:
   `source venv/bin/activate`.
4. Verify installation: `ws --help` should show the CLI usage.

Manual setup
------------

If you prefer to manage dependencies yourself:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
ws --help
```

Either path leaves you with the `ws` command (via `pip install -e .`) and the
core dependencies installed locally.
