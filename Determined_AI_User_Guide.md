<h1 align="center">Determined-AI User Guide</h1>
<p align="center">
2022-03-10 v0.1
</p>



# Introduction

!["intro-determined-ai"](https://docs.determined.ai/latest/_static/images/logo-determined-ai.svg)

We are currently using [Determined AI](https://www.determined.ai/) to manage our GPU Cluster.

You can open the dashboard (a.k.a WebUI) by the following URL and login:

[http://10.0.1.67:8080/](http://10.0.1.67:8080/)


# User Account

## Ask for your account

You need to ask system `admin` to get your user account. [[1]](https://docs.determined.ai/latest/sysadmin-basics/users.html)


## Authentication

### WebUI
The WebUI will automatically redirect users to a login page if there is no valid Determined session established on that browser. After logging in, the user will be redirected to the URL they initially attempted to access.

### CLI
Before using the CLI(Command Line Interface), you may need to recite some basics: [TODO:LinuxBasics]

In the CLI, the user login subcommand can be used to authenticate a user:

    det user login <username>

## Changing passwords
Users have *blank* passwords by default. This might be sufficient for low-security or experimental clusters, and it still provides the organizational benefits of associating each Determined object with the user that created it. If desired, a user can change their own password using the user change-password subcommand:

    det user change-password