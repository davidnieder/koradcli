# -*- coding: utf-8 -*-
"""Command-line interface for the Korad KA3005P power supply"""

import sys
from serial import SerialException

import click
from click import echo, style

from koradserial import KoradSerial


class OnOffChoice(click.Choice):
    def __init__(self):
        super(OnOffChoice, self).__init__(['on', 'off'])

def error(message):
    echo(style('Error: {0}'.format(message), fg='red'), err=True)

@click.group()
@click.pass_context
@click.option('-p', '--port', envvar='KORADPORT', prompt=True, help='Connect to this serial port.')
def korad(ctx, port):
    """Interfacing a Korad KA3005P power supply.

    If KORADPORT is in the environment, the --port option is optional:
    export KORADPORT=/dev/ttyACM0

    """
    try:
        global korad_device
        korad_device = KoradSerial(port)
    except SerialException as e:
        error(e)
        ctx.exit(1)

    ctx.call_on_close(korad_device.close)

@korad.command(help='Show the present status of the power supply.')
def status():
    echo(korad_device.status)

@korad.command(help='Show the korad model string.')
def model():
    echo(korad_device.model)

@korad.command(help='Turn power supply output on/off.')
@click.option('--read', is_flag=True, help='Show present output state.')
@click.argument('state', required=False, type=OnOffChoice(), metavar='[on|off]')
def output(state, read):
    if state:
        korad_device.output = state
    if read or not state:
        echo(korad_device.status.output)

@korad.command(help='Turn over-voltage-protection on/off.')
@click.option('--read', is_flag=True, help='Show whether device is in ovp mode or not.')
@click.argument('state', required=False, type=OnOffChoice(), metavar='[on|off]')
def ovp(state, read):
    if state:
        korad_device.ovp = state
    if read or not state:
        echo('ovp: {}'.format(korad_device.ovp))

@korad.command(help='Turn over-current-protection on/off.')
@click.option('--read', is_flag=True, help='Show whether device is in ocp mode or not.')
@click.argument('state', required=False, type=OnOffChoice(), metavar='[on|off]')
def ocp(state, read):
    if state:
        korad_device.ocp = state
    if read or not state:
        echo('ocp: {}'.format(korad_device.ocp))

@korad.command(help='Get/Set current target/real value.')
@click.option('--read', is_flag=True, help='Show present output current.')
@click.argument('current', required=False, type=float)
def current(current, read):
    if current:
        korad_device.current = current
    if read or not current:
        echo('Set: {0}, Actual: {1}'.format(korad_device.current_set, korad_device.current_actual))

@korad.command(help='Get/Set voltage target/real value.')
@click.option('--read', is_flag=True, help='Show presen output voltage.')
@click.argument('voltage', required=False, type=float)
def voltage(voltage, read):
    if voltage:
        korad_device.voltage = voltage
    if read or not voltage:
        echo('Set: {0}, Actual: {1}'.format(korad_device.voltage_set, korad_device.voltage_actual))

@korad.command(help='Save present values to device memory.')
@click.option('-m', required=True, type=click.IntRange(1,5), help='Number of memory bank to save to.')
def save(m):
    korad_device.save_to_memory(m)

@korad.command(help='Load values from device memory.')
@click.option('-m', required=True, type=click.IntRange(1,5), help='Number of memory bank to load from.')
def load(m):
    korad_device.recall_from_memory(m)
