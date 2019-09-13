# Sportsy, the sports catalog app

Do you ever feel like there are too many sports and an endless amount of sports equipment to go along with each one? Does it make you feel like :dizzy_face:, :cry:, or even :rage3:?

Sportsy can help you manage all of your sports inventory. It's a lightweight web app that manages your sports catalog by tracking sports categories and the items that go with each one.

## Setup

Running the Sportsy app is easy! The steps below guide you through setting up the virtual machine and how to run the app. 

First, download and install [Vagrant](https://www.vagrantup.com/) version 2.2.4. We’ll need these tools to setup and manage the Virtual Machine (VM).

```bash
# Install & Configure VM
vagrant up
```

```bash
# Log into machine
vagrant ssh
```

```bash
# Populate the database with sample data
cd /vagrant/catalog
python populate_catalog.py
```

Lastly, run the app locally with:

```bash
cd /vagrant/catalog
python application.py
```

The Sportsy app can now be accessed locally from your browser at `localhost:5000`.

**Note:** the Sportsy app is built on `python-2.7.12`.

## AWS Lightsail

As part of the Udacity Full-Stack Nanodegree program, this project is also hosted on AWS Lightsail, and can be accessed [here](http://34.212.32.68:80) or by entering the following into your browser: http://34.212.32.68:80

### Project Updates

This project was linked to the [Configuring Linux Web Servers](https://classroom.udacity.com/courses/ud299) course which tought me how to secure and configure a Linux server. The summary of steps taken for this specific project were as follows:

#### Server Setup

##### Initial steps

1. Visit https://lightsail.aws.amazon.com to create an Ubuntu 16.04 instance.
2. Create a new user for "grader" and grant this user permissions.
3. Disable SSH password authorization, and enable key-based access by generating (`ssh-keygen`) and copying public SSH keys.
4. Update the SSH port to use a non-default port. 
5. Configure the uncomplicated firewall (UFW) for SSH, HTTP, and NTP.

##### PostgreSQL

1. Install `postgresql`, and verify that no remote connections are allowed.
2. Create a new database and user, and set user password and permissions.

##### Project Setup

1. Install `git` and clone the project into `/var/www`
2. Update references to database engine (replacing SQLite with PostgreSQL).
3. Create the database schema with the `populate_catalog.py` script.

##### Apache

1. Install `apache2` and `mod_wsgi`.
2. Create and configure `catalog.wsgi` script in `/var/www`.
3. Enable the virtual host with `sudo a2ensite catalog`.
4. Restart the Apache service.

#### Third Party Resources

The following resources were crucial to the success of this project:

- Stack Overflow
- The [mod_wsgi](https://modwsgi.readthedocs.io/en/develop/user-guides) user guides
