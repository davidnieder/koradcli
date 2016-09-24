# -*- coding: utf-8 -*-
"""Tests for koradserial.py and koradcli.py

The power supply needs to be connected.
serial_port needs to be set correctly.

"""

from unittest import TestCase, main
from click.testing import CliRunner

from koradserial import KoradSerial, OnOffState, OutputMode
from koradcli import korad


serial_port = '/dev/ttyACM0'

class KoradSerialTest(TestCase):

    def setUp(self):
        self.ps = KoradSerial(serial_port)
        self.ps.output = OnOffState('off')

    def tearDown(self):
        self.ps.close()

    def test_modelstring(self):
        model = self.ps.model
        self.assertTrue(model.startswith('KORAD') or model.startswith('VELLEMAN'))

    def test_statusclass(self):
        status = self.ps.status

        self.assertIsInstance(status.mode, OutputMode)
        self.assertIsInstance(status.beep, OnOffState)
        self.assertIsInstance(status.ocp, OnOffState)
        self.assertIsInstance(status.ovp, OnOffState)
        self.assertIsInstance(status.output, OnOffState)

    def test_ocp(self):
        self.ps.ocp = OnOffState('on')
        self.assertEqual(self.ps.ocp.name, 'on')
        self.ps.ocp = 'off'
        self.assertEqual(self.ps.ocp.name, 'off')

    def test_ovp(self):
        self.ps.ovp = OnOffState('on')
        self.assertEqual(self.ps.ovp.name, 'on')
        self.ps.ovp = 'off'
        self.assertEqual(self.ps.ovp.name, 'off')

    def test_output(self):
        self.ps.output = OnOffState('off')
        self.assertEqual(self.ps.output.name, 'off')
        self.ps.output = 'on'
        self.assertEqual(self.ps.output.name, 'on')

    def test_voltage(self):
        self.ps.output = OnOffState('off')
        voltage = self.ps.voltage_set
        self.ps.voltage = 1

        self.assertEqual(self.ps.voltage_actual, 0)
        self.assertEqual(self.ps.voltage_set, 1)

        self.ps.voltage = voltage

    def test_current(self):
        self.ps.output = OnOffState('off')
        current = self.ps.current_set
        self.ps.current = 1

        self.assertEqual(self.ps.current_actual, 0)
        self.assertEqual(self.ps.current_set, 1)

        self.ps.current = current

    def test_memory(self):
        # remember saved values
        self.ps.recall_from_memory(1)
        c1, v1 = self.ps.current_set, self.ps.voltage_set
        self.ps.recall_from_memory(2)
        c2, v2 = self.ps.current_set, self.ps.voltage_set

        self.ps.current = 2.0
        self.ps.voltage = 5.0
        self.ps.save_to_memory(1)

        self.ps.current = 0.5
        self.ps.voltage = 3.3
        self.ps.save_to_memory(2)

        self.ps.recall_from_memory(1)
        self.assertEqual(self.ps.current_set, 2.0)
        self.assertEqual(self.ps.voltage_set, 5.0)

        self.ps.recall_from_memory(2)
        self.assertEqual(self.ps.current_set, 0.5)
        self.assertEqual(self.ps.voltage_set, 3.3)

        self.ps.current = 1.5
        self.ps.voltage = 8.0
        self.ps.save_to_memory(1)

        self.ps.current = 0.2
        self.ps.voltage = 15.0
        self.ps.save_to_memory(2)

        self.ps.recall_from_memory(1)
        self.assertEqual(self.ps.current_set, 1.5)
        self.assertEqual(self.ps.voltage_set, 8.0)

        self.ps.recall_from_memory(2)
        self.assertEqual(self.ps.current_set, 0.2)
        self.assertEqual(self.ps.voltage_set, 15.0)

        # set backed up values
        self.ps.current, self.ps.voltage = c2, v2
        self.ps.save_to_memory(2)
        self.ps.current, self.ps.voltage = c1, v1
        self.ps.save_to_memory(1)


class KoradCliTest(TestCase):

    def setUp(self):
        self.runner = CliRunner(env={'KORADPORT': serial_port})

    def test_model(self):
        result = self.runner.invoke(korad, ['model'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith('KORAD') or \
                        result.output.startswith('VELLEMAN'))

    def test_status(self):
        result = self.runner.invoke(korad, ['status'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('Output:' in result.output)
        self.assertTrue('Mode:' in result.output)
        self.assertTrue('OVP:' in result.output)
        self.assertTrue('OCP:' in result.output)
        self.assertTrue('Beep:' in result.output)

    def test_ovp(self):
        result = self.runner.invoke(korad, ['ovp'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('on' in result.output or 'off' in result.output)

    def test_ocp(self):
        result = self.runner.invoke(korad, ['ocp'])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue('on' in result.output or 'off' in result.output)

    def test_output(self):
        result = self.runner.invoke(korad, ['output', '--read', 'on'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'on\n')

        result = self.runner.invoke(korad, ['output', '--read', 'off'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'off\n')

    def test_voltage(self):
        result = self.runner.invoke(korad, ['voltage', '1'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '')

        result = self.runner.invoke(korad, ['voltage'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Set: 1.0, Actual: 0.0\n')

        result = self.runner.invoke(korad, ['voltage', '--read', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Set: 2.0, Actual: 0.0\n')

    def test_current(self):
        result = self.runner.invoke(korad, ['current', '1'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '')

        result = self.runner.invoke(korad, ['current'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Set: 1.0, Actual: 0.0\n')

        result = self.runner.invoke(korad, ['current', '--read', '2'])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, 'Set: 2.0, Actual: 0.0\n')


if __name__ == '__main__':
    main()
