# -*- coding: utf-8 -*-
"""Serial communication with the Korad KA3005P power supply

This is a rewrite of koradserial.py from
https://github.com/starforgelabs/py-korad-serial
Thanks to starforgelabs for his project

Example usage:
    ps = KoradSerial('/dev/ttyACM0')
    ps.current = 0.5
    ps.voltage = 3.3
    ps.output = 'on'
    ps.close()

"""

from time import sleep
from serial import Serial as PySerial


class State(object):
    states = []

    def __init__(self, state):
        for el in self.states:
            if state in el:
                self.state = el
                self.value = el[0]
                self.name = el[1]
                return
        raise ValueError()

    def __repr__(self):
        return '<{0}: {1}>'.format(self.__class__.__name__, self.name)

    def __str__(self):
        return '{}'.format(self.name)

    def __eq__(self, other):
        if isinstance(other, State):
            return self.value == other.value and self.name == other.name
        else:
            return self.value == other or self.name == other


class OnOffState(State):
    states = [(0, 'off'), (1, 'on')]

on_state = OnOffState('on')
off_state = OnOffState('off')


class OutputMode(State):
    states = [(0, 'constant current'), (1, 'constant voltage')]


class KoradStatus(object):
    """Class representing the Korad status byte"""

    def __init__(self, status_byte):
        self.raw = status_byte
        self.mode = OutputMode(status_byte & 1)
        self.beep = OnOffState((status_byte >> 4) & 1)

        self.ocp = OnOffState((status_byte >> 5) & 1)
        self.output = OnOffState((status_byte >> 6) & 1)
        self.ovp = OnOffState((status_byte >> 7) & 1)

    def __repr__(self):
        return '{0:b}'.format(self.raw)

    def __str__(self):
        return 'Output: {0}\nMode: {1}\nOVP: {2}\nOCP: {3}\nBeep: {4}'.format(
            self.output, self.mode, self.ovp, self.ocp, self.beep)


class Serial(PySerial):
    """Small convenience wrapper around pyserial"""

    def __init__(self, port, wait):
        super(Serial, self).__init__(port=port, baudrate=9600, timeout=.1)
        self.wait = wait

    def send(self, data):
        sleep(self.wait)
        return self.write(data)

    def send_receive(self, data):
        self.send(data)
        self.flush()

        response = str()
        c = self.read()
        while c != '':
            response += c
            c = self.read()
        return response


class KoradSerial(object):
    """Python interface to the power supply"""

    def __init__(self, serial_port, wait=.05):
        self.port = Serial(serial_port, wait)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.port.close()
        return False

    def close(self):
        self.port.close()

    @property
    def model(self):
        return self.port.send_receive("*IDN?")

    @property
    def status(self):
        return KoradStatus(ord(self.port.send_receive('STATUS?')))

    @property
    def voltage_set(self):
        return float(self.port.send_receive('VSET1?'))

    @property
    def voltage_actual(self):
        return float(self.port.send_receive('VOUT1?'))

    voltage = voltage_actual
    @voltage.setter
    def voltage(self, value):
        self.port.send('VSET1:{0:05.2f}'.format(value))

    @property
    def current_set(self):
        return float(self.port.send_receive('ISET1?')[:5])

    @property
    def current_actual(self):
        return float(self.port.send_receive('IOUT1?'))

    current = current_actual
    @current.setter
    def current(self, value):
        self.port.send('ISET1:{0:05.3f}'.format(value))

    @property
    def ovp(self):
        return self.status.ovp

    @ovp.setter
    def ovp(self, state):
        if not isinstance(state, OnOffState):
            state = OnOffState(state)
        self.port.send('OVP{0}'.format(state.value))

    @property
    def ocp(self):
        return self.status.ocp

    @ocp.setter
    def ocp(self, state):
        if not isinstance(state, OnOffState):
            state = OnOffState(state)
        self.port.send('OCP{0}'.format(state.value))

    @property
    def output(self):
        return self.status.output

    @output.setter
    def output(self, state):
        if not isinstance(state, OnOffState):
            state = OnOffState(state)
        self.port.send('OUT{0}'.format(state.value))

    @property
    def output_mode(self):
        return self.status.mode

    @property
    def beep(self):
        return self.status.beep

    def save_to_memory(self, memory_bank):
        # the power supply won't save to a memory bank if it wasn't loaded before
        current, voltage, output = self.current_set, self.voltage_set, self.output
        if output == on_state:
            # turn output off before recalling old values
            self.output = off_state

        # load from memory, set values and finally do actual save
        self.recall_from_memory(memory_bank)
        self.current = current
        self.voltage = voltage
        self.port.send('SAV{0}'.format(memory_bank))

        if output == on_state:
            # set back original output state
            self.output = on_state

    def recall_from_memory(self, memory_bank):
        self.port.send('RCL{0}'.format(memory_bank))
