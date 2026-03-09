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

### Via HACS (Recommended)
1. Ensure [HACS](https://hacs.xyz/) is installed.
2. Go to **HACS -> Integrations -> 3 dots (top right) -> Custom repositories**.
3. Add `https://github.com/ILC0nte/Gree-PDC-Custom-Component` as a **Repository** and select **Integration** as the **Category**.
4. Click **Add**, then find "Gree PDC" in HACS and click **Download**.
5. Restart Home Assistant.
6. Add the integration via **Settings -> Devices & Services -> Add Integration -> Gree PDC**.

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

### Control & Configuration
- `switch.gree_power_switch`: Main power control.
- `switch.gree_quiet_mode_switch`: Quiet mode toggle.
- `select.gree_operation_mode`: Mode selection (Heating, Cooling, DHW, and hybrid modes).
- `number.gree_setpoint_dhw`: DHW target temperature.
- `number.gree_setpoint_heating_out_temp`: Target flow temperature for heating.
- `number.gree_setpoint_cooling_out_temp`: Target flow temperature for cooling.
- `number.gree_setpoint_heating_room_temp`: Target room temperature for heating.
- `number.gree_setpoint_cooling_room_temp`: Target room temperature for cooling.

### Monitoring
- `sensor.gree_in_water_temp`: Incoming water temperature (return).
- `sensor.gree_out_water_temp`: Outgoing water temperature (flow).
- `sensor.gree_temp_dhw`: Domestic Hot Water tank temperature.
- `sensor.gree_room_temp`: Current room temperature.
- `sensor.gree_operation_mode`: Localized current operation mode text.

### Status Indicators
- `binary_sensor.gree_heating_state`: Active when the unit is heating.
- `binary_sensor.gree_cooling_state`: Active when the unit is cooling.
- `binary_sensor.gree_dhw_state`: Active when producing Hot Water.
- `binary_sensor.gree_boiler_heat_resistance`: Status of the DHW electric heater.
- `binary_sensor.gree_rapid_dhw`: Status of the "Fast Hot Water" function.
- `binary_sensor.gree_defrost_cycle`: Active during the defrost cycle.
- `binary_sensor.gree_antifreeze_function`: Status of the antifreeze protection.
- `binary_sensor.gree_power`: General power status.
- `binary_sensor.gree_quiet_mode`: General quiet mode status.

## Tested Devices 
Component where tested and confirmed to work for:
- Aermec HMI series (my own heat pump!)
- Hokkaido Ondo series
- Rhoss Thaity series

## Credits
This project is based on the work of several contributors and projects:

gree-remote - Gree air conditioner remote control protocol
Home Assistant Developer Documentation - Official development guidelines and best practices

* [gree-remote](https://github.com/tomikaa87/gree-remote) - Gree air conditioner remote control protocol.
* [Home Assistant Developer Documentation](https://developers.home-assistant.io/) - Official development guidelines and best practices
* [Google Antigravity Ide](https://antigravity.google/)
