# DK - modules in the first line are obsolete. Import classes used in PIDModelGeneric -> https://github.com/PyMoDAQ/PyMoDAQ/blob/6daca234d2ba46a09f1ccebc9e982cb1b029d9ee/src/pymodaq/extensions/pid/utils.py#L32
# AD -> don't need to import since the class inherits from PIDModelGeneric
from typing import List
import numpy as np
from pymodaq.extensions.pid.utils import PIDModelGeneric, main
from pymodaq.utils.data import DataActuator, DataToExport, DataCalculated, DataToActuators

import logging
logger = logging.getLogger(__name__)

# def power_covert_to_position(outputs: List[float], dt: float, stab=True):
#     """ Should be replaced here or in the model class to process the outputs """
#     #TODO: No simple way to do this
#     return outputs

# Dk - Comment out
# def some_function_to_convert_the_data(measurements: DataToExport):
#     """ Should be replaced here or in the model class to process the measurement """
#     a = 0
#     b = 1
#     return [a, b]

class PIDModelOptoLaser(PIDModelGeneric):
    limits = dict(max=dict(state=False, value=100),
                  min=dict(state=False, value=-100),)
    konstants = dict(kp=0.1, ki=0.000, kd=0.0000)

    Nsetpoints = 1  # number of setpoints
    setpoint_ini = [1e-9]  # number and values of initial setpoints
    setpoints_names = ['power']  # number and names of setpoints

    actuators_name = ['Move 00']  # names of actuator's control modules involved in the PID
    detectors_name = ['Det 00']  # names of detector's control modules involved in the PID

    # Target Power will be set in setpoint. Delete this dictionary. We only need wavelength at this moment.
    params = [ {'title': 'Wavelength', 'name': 'wavelength', 'type': 'float', 'value': 532}]

    def __init__(self, pid_controller):
        super().__init__(pid_controller)
        # self.power = 0

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == 'wavelength': # DK - correct typo
            self.settings['wavelength'] = param.value() # DK - the wavelength setting in the powermeter was not updated.

    def ini_model(self):
        super().ini_model()

    def convert_input(self, measurements: DataToExport):
        """
        Convert the measurements in the units to be fed to the PID (same dimensionality as the setpoint)
        Parameters
        ----------
        measurements: DataToExport
            Data from the declared detectors from which the model extract a value of the same units as the setpoint

        Returns
        -------
        DataToExport: the converted input in the setpoints units

        """
        # power = measurements.data[0] # Edit
        #get_data_from_dim(dim='Data0D')#[0][0]
        power = measurements.get_data_from_dim('Data0D')[0][0]
        self.curr_input = [power]
        # logger.info("Current input: {}".format(self.curr_input))
        return DataToExport('inputs',
                    data=[DataCalculated(self.setpoints_names[ind],
                                         data=[self.curr_input[ind]]) # np.array([power])
                          for ind in range(len(self.setpoints_names))])


    def convert_output(self, outputs: List[float], dt: float, stab=True):
        """
        Convert the output of the PID in units to be fed into the actuator
        Parameters
        ----------
        outputs: List of float
            output value from the PID from which the model extract a value of the same units as the actuator
        dt: float
            Ellapsed time since the last call to this function
        stab: bool

        Returns
        -------
        DataToActuators: the converted output

        """
        # DK - Fix. The actuator value in the GUI does not match the actuator value in physical instrument
        self.curr_output = np.array(outputs)
        return DataToActuators('pid', mode='rel',
                         data=[DataActuator(self.actuators_name[ind], data=[self.curr_output])
                               for ind in range(len(self.curr_output))])


if __name__ == '__main__':
    # main("OptoControllerModel.xml")
    main()