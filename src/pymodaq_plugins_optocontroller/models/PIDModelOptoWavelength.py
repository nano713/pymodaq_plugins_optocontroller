from pymodaq.extensions.pid.utils import PIDModelGeneric, main
from pymodaq.utils.data import DataToExport
from typing import List
import numpy as np
from pymodaq.utils.data import DataActuator, DataToExport, DataCalculated, DataToActuators
from pymodaq_plugins_thorlabs.daq_viewer_plugins.plugins_1D.daq_1Dviewer_CCSXXX import DAQ_1DViewer_CCSXXX
from pymodaq_plugins_zaber.daq_move_plugins.daq_move_Zaber import DAQ_Move_Zaber


def some_function_to_convert_the_pid_outputs(outputs: List[float], dt: float, stab=True):
    """ Should be replaced here or in the model class to process the outputs """
    return outputs


def some_function_to_convert_the_data(measurements: DataToExport):
    """ Should be replaced here or in the model class to process the measurement """
    a = 0
    b = 1
    return [a, b]


class PIDModelOptoWave(PIDModelGeneric):
    limits = dict(max=dict(state=False, value=100),
                  min=dict(state=False, value=-100),)
    konstants = dict(kp=0.1, ki=0.000, kd=0.0000)

    Nsetpoints = 1  # number of setpoints
    setpoint_ini = [128]  # number and values of initial setpoints
    setpoints_names = ['wavelength']  # number and names of setpoints

    actuators_name = ["Move 00"]  # names of actuator's control modules involved in the PID
    detectors_name = ['Det 01']  # names of detector's control modules involved in the PID

    param_zaber = DAQ_1DViewer_CCSXXX.params
    param_csthorlabs = DAQ_Move_Zaber.params

    params = param_zaber + param_csthorlabs

    def __init__(self, pid_controller):
        super().__init__(pid_controller)

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == 'integration_time':
            controller = self.modules_manager.get_mod_from_name('Det 01').controller
            controller.time = self.settings.child('integration_time').value()
            self.settings.child('integration_time').setValue(controller.time)  

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

        wavelength = measurements.get_data_from_dim('Data1D')[0][0] # <- we get an intensity 1D array from this method
        """
        wavelength (1D array) <- 
        intensity (1D array)

        Apply Lorentzian fit to intensity vs. wavelength to extract the peak center_wavelength

        data = [center_wavelength] in DataToExport
        """

        self.curr_input = [wavelength]
        return DataToExport('inputs',
                    data=[DataCalculated(self.setpoints_names[ind],
                                         data=[self.curr_input[ind]]) 
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
        OutputToActuator: the converted output

        """
        self.curr_output = np.array(outputs)
        return DataToActuators('pid', mode='rel',
                         data=[DataActuator(self.actuators_name[ind], data=[self.curr_output])
                               for ind in range(len(self.curr_output))])


if __name__ == '__main__':
    main("BeamSteeringMockNoModel.xml")  # some preset configured with the right actuators and detectors

