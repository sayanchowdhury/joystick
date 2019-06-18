## Joystick

Joystick is a fedora-messaging consumer that listens to `org.fedoraproject.prod.pungi.compose.status.change`. The application processes the messages, the extract out the required metadata and call `plume` with the required arguments. The project is in active development state

### Development Guide

If you would like to write a patch for Joystick, this document will help you get started.

#### Quick Development setup

We would be using virtualenv to setup the project. Joystick uses Python3.

Clone the repo:

```
git clone https://pagure.io/joystick
cd joystick
```

Setup the Python3 virtualenv:

```
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
```

Install the development dependencies:
```
python3 setup.py develop
```

Start the fedora-messaging consumer:
```
fedora-messaging --conf joystick.toml consume
```

#### Running the tests

You can run the unit-tests, which live in the `joystick.tests` package, with the following command:

```
python3 -m pytest joystick
```

To generate the test coverage report, run the following command:

```
python3 -m pytest --cov=joystick --cov-report html joystick
cd htmlcov
python3 -m http.server
```

Once the last command fires up the server, head over to `http://localhost:8000/` in your browser.

### Copyright and License

This project is copyright Red Hat and other contributors, licensed under the terms of the GNU General Public License version 3. See the `LICENSE` file for the complete text of the license. Refer to the git history for complete authorship details
