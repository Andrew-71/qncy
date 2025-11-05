# QNCY

This is the repository for my question & answer platform, developed as
Web Technologies homework at VK Education.

## Test data

To start a new db with mock data and n users (assuming no db exists yet),
do the following:

```sh
python manage.py migrate
python manage.py fill_db <n>
```

Passwords for all users is `demopassword`.
