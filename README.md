## Joystick

Joystick is a fedora-messaging consumer that listens to `org.fedoraproject.prod.pungi.compose.status.change`. The application processes the messages, the extract out the required metadata and call `plume` with the required arguments. The project is in active development state

### Development 

```
git clone https://pagure.io/joystick
cd joystick
python3 setup.py develop
fedora-messaging --conf joystick.toml consume
```

### Tests

```
pytest tests/
```


