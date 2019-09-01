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
