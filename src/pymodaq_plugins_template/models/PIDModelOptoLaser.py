# DK - modules in the first line are obsolete. Import classes used in PIDModelGeneric -> https://github.com/PyMoDAQ/PyMoDAQ/blob/6daca234d2ba46a09f1ccebc9e982cb1b029d9ee/src/pymodaq/extensions/pid/utils.py#L32
# AD -> don't need to import since the class inherits from PIDModelGeneric
from pymodaq.extensions.pid.utils import PIDModelGeneric, OutputToActuator, InputFromDetector, main
from pymodaq.utils.data import DataToExport
from typing import List



# DK - comment out
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

# Rename PIDModelTemplate
class PIDModelOptoLaser(PIDModelGeneric):
    limits = dict(max=dict(state=False, value=100),
                  min=dict(state=False, value=-100),)
    konstants = dict(kp=0.1, ki=0.000, kd=0.0000)

    # DK - Nsetpoints = 1 because we move only one axis
    Nsetpoints = 2  # number of setpoints
    # DK - [xxx] one element
    setpoint_ini = [128, 128]  # number and values of initial setpoints
    # DK - ["xxx"] one element
    setpoints_names = ['Xaxis', 'Yaxis']  # number and names of setpoints

    actuators_name = ["X-KDC"]  # names of actuator's control modules involved in the PID
    detectors_name = ['PowerMeter']  # names of detector's control modules involved in the PID

    # Target Power will be set in setpoint. Delete this dictionary. We only need wavelength at this moment.
    params = [{'title': 'Target Power', 'name': 'power', 'type': 'float', 'value': 0.01}, 
              {'title': 'Wavelength', 'name': 'wavelength', 'type': 'float', 'value': 0.001}] 

    def __init__(self, pid_controller):
        super().__init__(pid_controller)
        self.power = 0

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == 'power':
            self.settings['power'] = param.value()
        if param.name() == 'wavelength': # DK - correct typo
            self.settings['wavelength'] = param.value()

    def ini_model(self):
        super().ini_model()

        # add here other specifics initialization if needed

    def convert_input(self, measurements: DataToExport):
        """
        Convert the measurements in the units to be fed to the PID (same dimensionality as the setpoint)
        Parameters
        ----------
        measurements: DataToExport
            Data from the declared detectors from which the model extract a value of the same units as the setpoint

        Returns
        -------
        InputFromDetector: the converted input in the setpoints units

        """
        power = measurements.get_data_from_dim('PowerMeter')[0][0]
        power = power - self.settings['power']
        self.power = power
        #x, y = some_function_to_convert_the_data(measurements)
        return InputFromDetector(values=[power]) # DK - return in DataToExport object

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
        OutputToActuator: the converted output

        """
        # outputs = power_covert_to_position(outputs, dt, stab)
        # return OutputToActuator(mode='rel', values=outputs)
        #  DK restore return. Return in DataToActuators object.
        pass 


if __name__ == '__main__':
    # DK - rename .xml file although we have not created this xml yet.
    main("OptoControllerModel.xml")  # some preset configured with the right actuators and detectors
