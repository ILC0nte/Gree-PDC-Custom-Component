# Gree PDC Custom Component for Home Assistant

Custom component for Home Assistant to control and monitor Gree Heat Pumps (PDC) via local UDP protocol.

## Features
- **Auto-Discovery**: Automatic scanning for Gree devices on the network during configuration.
- **Multi-Device Support**: Ability to configure and manage multiple heat pumps.
- **Custom Naming**: Choose a custom name for each device to prefix all its entities (e.g., "Main Heat Pump").
- **Multilingual Support**: Full support for English and Italian translations for all entities and operation modes.
- **Configurable Polling**: Adjustable status update interval (5 to 600 seconds).
- **Monitoring**: Comprehensive monitoring of water temperatures (In/Out/DHW), room temperature, and internal status registers.
- **Control**: 
    - Power and Quiet mode.
    - Operation mode selection (Heating, Cooling, DHW, and hybrid modes).
    - Setpoint adjustments for DHW, Flow, and Room temperatures.

## Installation
### Manual
1. Copy the `custom_components/gree_pdc` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via **Settings -> Devices & Services -> Add Integration -> Gree PDC**.

## Configuration
The setup process is now streamlined:
1. Enter the **IP Address** of the PDC.
2. Select the desired device from the list of discovered units.
3. Specify a **Device Name** (this will be used as a prefix for all entity names).
4. (Optional) Adjust the **Polling Interval** in the integration options.

## Entities
The component generates a prefixed set of entities (example for a device named "Gree"):
- `switch.gree_power_switch`: Main power control.
- `switch.gree_quiet_mode_switch`: Quiet mode toggle.
- `select.gree_operation_mode`: Mode selection with localized options.
- `sensor.gree_pdc_mode`: Localized current operation mode sensor.
- `binary_sensor.gree_heating_state`: ON when heating function is active.
- `binary_sensor.gree_cooling_state`: ON when cooling function is active.
- `binary_sensor.gree_dhw_state`: ON when DHW (ACS) function is active.
- `sensor.gree_out_water_temp`: Current flow temperature.
- `number.gree_setpoint_dhw`: DHW target temperature.

## Credits
Based on the original reverse engineering of the Gree UDP protocol.
