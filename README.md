# koradcli
Command-line interface for the Korad KA3005P power supply.
Compatible Korad or Velleman devices probably work but are not tested.

### Install with python-setuptools
> python2 setup.py

### Example usage
```
# set KORADPORT envvar for convenience
export KORADPORT=/dev/ttyACM0
# set voltage/current (5V/0.5A)
korad voltage 5
korad current 0.5
# turn output on
korad output on
# save this values to "M1"
korad save -m 1
```

### Help page
```
Usage: korad [OPTIONS] COMMAND [ARGS]...

  Interfacing a Korad KA3005P power supply.

  If KORADPORT is in the environment, the --port option is optional: export
  KORADPORT=/dev/ttyACM0

Options:
  -p, --port TEXT  Connect to this serial port.
  --help           Show this message and exit.

Commands:
  current  Get/Set current target/real value
  load     Load values from device memory
  model    Show the korad model string.
  ocp      Turn over-current-protection on/off.
  output   Turn power supply output on/off.
  ovp      Turn over-voltage-protection on/off.
  save     Save present values to device memory
  status   Show the present status of the power supply.
  voltage  Get/Set voltage target/real value
```

### Made with
- [click](http://click.pocoo.org/)
- [pyserial](https://github.com/pyserial/pyserial)
- [py-korad-serial](https://github.com/starforgelabs/py-korad-serial)
