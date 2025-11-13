# QNCY

This is the repository for my question & answer platform, developed as
Web Technologies homework at VK Education.

## Deployment

If you have Docker installed and are fine with temporarily losing ~1.5gb of
space, you can deploy a fully working instance of the app by running the
following command:

```sh
sh deploy.sh
```

This will create a docker stack named `vk-web` with a working server
pre-populated with 25 fake users and mock data.
Passwords for all users is `demopassword`.
