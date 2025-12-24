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

By default, the system starts with an SQLite3 database. This can be changed
by populating the environment variables and more specifically setting
`QNCY_DB_BACKEND=postgres`. For a quick demo, use `deploy.sh`.

To add mock user data, a management command `fill_db [ratio]` is present.
Sidebar data can updated using `generate_sidebar`.

### Docker

If you have Docker installed and are fine with losing ~1.5gb of space, you can
deploy a fully working instance of the app using the compose file provided.