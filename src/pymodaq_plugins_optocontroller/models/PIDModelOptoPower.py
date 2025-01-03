from typing import List
import numpy as np
from pymodaq.extensions.pid.utils import PIDModelGeneric, main
from pymodaq.utils.data import DataActuator, DataToExport, DataCalculated, DataToActuators
from pymodaq.utils.parameter import utils
from pymodaq_plugins_thorlabs.hardware.powermeter import CustomTLPM, DEVICE_NAMES
from pymodaq_plugins_thorlabs.daq_viewer_plugins.plugins_0D.daq_0Dviewer_TLPMPowermeter import DAQ_0DViewer_TLPMPowermeter

class PIDModelOptoPower(PIDModelGeneric):
    limits = dict(max=dict(state=False, value=100),
                  min=dict(state=False, value=-100),)
    konstants = dict(kp=0.1, ki=0.000, kd=0.0000)

    param_power = DAQ_0DViewer_TLPMPowermeter.params

    Nsetpoints = 1  # number of setpoints
    setpoint_ini = [1e-9]  # number and values of initial setpoints
    setpoints_names = ['power']  # number and names of setpoints

    actuators_name = ['Move 00']  # names of actuator's control modules involved in the PID
    detectors_name = ['Det 00']  # names of detector's control modules involved in the PID

    params = param_power
    def __init__(self, pid_controller):
        super().__init__(pid_controller)
        self.power = None
    

    def update_settings(self, param):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        if param.name() == 'wavelength':
            controller = self.modules_manager.get_mod_from_name('Det 00').controller
            controller.wavelength = self.settings.child('wavelength').value()
            self.settings.child('wavelength').setValue(controller.wavelength)            

    def ini_model(self):
        super().ini_model()
        self.power = DAQ_0DViewer_TLPMPowermeter()
    
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
        power = measurements.get_data_from_dim('Data0D')[0][0]
        self.curr_input = [power]
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
        DataToActuators: the converted output

        """
        self.curr_output = np.array(outputs)
        return DataToActuators('pid', mode='rel',
                         data=[DataActuator(self.actuators_name[ind], data=[self.curr_output])
                               for ind in range(len(self.curr_output))])

if __name__ == '__main__':
    main()
