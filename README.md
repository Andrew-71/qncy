# QNCY

This is the repository for my question & answer platform, developed as
Web Technologies homework at VK Education.

## Test data

Until a script to auto-generate data is written, sample data is provided.
To start a new db with it (assuming no db exists yet), do the following:

```sh
python manage.py migrate
python manage.py loaddata testdata.json
```

Passwords for all users is `demouser`.
The administrator account is called `demouser`.
