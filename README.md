# QNCY

This is the repository for my question & answer platform, developed as
Web Technologies homework at VK Education.

## Development

The development environment is set up like this:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

Useful command: `pre-commit run --all-files`

## Deployment

To add mock user data, a management command `fill_db [ratio]` is present.
Sidebar data can updated using `generate_sidebar`.

The project contains many parts (PostgreSQL, Centrifugo, Redis, etc.).
As such, `docker.sh` is recommended for a quick demo deployment.
