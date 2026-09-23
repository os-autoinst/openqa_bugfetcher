# openqa_bugfetcher

Tool to update the openqa bug status cache


## Installation

```sh
python3 setup.py install
```


## Configuration

You will need to configure your openQA API Key in `/etc/openqa/client.conf`:

```cfg
[openqa.opensuse.org]
key = FOO
secret = BAR
```

Then you will need to edit `/etc/openqa/bugfetcher.conf` and set up the desired openQA server
and bugtracker login information.


## Running

Just run `fetch_openqa_bugs` (you can set it up as a cron for every 10min - it will only refresh the bugs that haven't been refreshed
within the timespan configured in `bugfetcher.conf`)


## Systemd Integration

There are systemd units/timers provided which can be installed locally:

```sh
$ sudo make install-systemd-local
$ sudo systemctl daemon-reload
$ sudo systemctl enable --now openqa_bugfetcher@opensuse.org.timer
```


## Contribute

Feel free to add issues or send pull requests.

### Local testing

#### Style and type checks

Run style, type, and code health checks:

```sh
make checkstyle
```

To format code and fix linting issues:

```sh
make tidy
```
