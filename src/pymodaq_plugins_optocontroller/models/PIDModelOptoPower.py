# DK - modules in the first line are obsolete. Import classes used in PIDModelGeneric -> https://github.com/PyMoDAQ/PyMoDAQ/blob/6daca234d2ba46a09f1ccebc9e982cb1b029d9ee/src/pymodaq/extensions/pid/utils.py#L32
# AD -> don't need to import since the class inherits from PIDModelGeneric
from typing import List
import numpy as np
from pymodaq.extensions.pid.utils import PIDModelGeneric, main
from pymodaq_gui.parameter import Parameter
from pymodaq.utils.data import DataActuator, DataToExport, DataCalculated, DataToActuators
from pymodaq.utils.parameter import utils
from pymodaq_plugins_thorlabs.hardware.powermeter import CustomTLPM, DEVICE_NAMES
from pymodaq_plugins_thorlabs.daq_viewer_plugins.plugins_0D.daq_0Dviewer_TLPMPowermeter import DAQ_0DViewer_TLPMPowermeter


# def power_covert_to_position(outputs: List[float], dt: float, stab=True):
#     """ Should be replaced here or in the model class to process the outputs """
#     #TODO: No simple way to do this
#     return outputs


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

    # Target Power will be set in setpoint. Delete this dictionary. We only need wavelength at this moment.
    params = param_power
    # [ {'title': 'Wavelength', 'name': 'wavelength', 'type': 'float', 'value': 532}]

    def __init__(self, pid_controller):
        super().__init__(pid_controller)
        #DAQ_0DViewer_TLPMPowermeter.__init__()

        self.power = None
        self.controller = None
        #self.power = DAQ_0DViewer_TLPMPowermeter()
        # self.controller = None
        # print(f"{self.power} is initialized")
    def controller_initialization(self):
        """
        Initialize the controller
        """
        index = DEVICE_NAMES.index(self.settings['devices'])
        self.controller = CustomTLPM()
        info = self.controller.infos.get_devices_info(index)
        self.controller.open_by_index(index)
        self.settings.child('info').setValue(str(info))

        self.settings.child('wavelength').setOpts(limits=self.controller.wavelength_range)
        self.controller.wavelength = self.settings.child('wavelength').value()
        self.settings.child('wavelength').setValue(self.controller.wavelength)

    def update_settings(self, param: Parameter):
        """
        Get a parameter instance whose value has been modified by a user on the UI
        Parameters
        ----------
        param: (Parameter) instance of Parameter object
        """
        super().update_settings(param)
        if 'wavelength' in utils.get_param_path(param):
            self.power.commit_settings(param)
        # if param.name() == 'wavelength': # DK - correct typo
        #     self.settings['wavelength'] = self.power.commit_settings(self.settings['wavelength'])
    def ini_model(self):
        super().ini_model()
        self.power = DAQ_0DViewer_TLPMPowermeter()
        # self.power.ini_detector(controller = None)
       
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
        self.curr_output = np.array(outputs)
        return DataToActuators('pid', mode='rel',
                         data=[DataActuator(self.actuators_name[ind], data=[self.curr_output])
                               for ind in range(len(self.curr_output))])

if __name__ == '__main__':
    # main("OptoControllerModel.xml") 
    main()
