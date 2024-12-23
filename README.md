JHF Powerfail
=============

In our house we have a Sol-Ark 15K inverter with a relatively small
battery (7.5kWh) and an 8.75kW inverter generator that is controlled
by the Sol-Ark.  The main heating system is an air-source heat pump,
with a propane furnace for backup heat.  The HVAC system is controlled
by an Ecobee thermostat with the the propane furnace configured as
"aux" heat.

When the power goes out, I need to switch the Ecobee into aux-heat
only mode as the batteries cannot run the heat pump for very long, and
the inverter generator we have cannot charge the batteries and run the
heat pump at the same time.

Similarly, when the power comes back on I would like to set the Ecobee
thermostat back to automatic mode.

This repository contains scripts and code (mostly/completely in
python) to implement this.  Where authentication material is needed,
it is storted in the "jhf-powerfail.conf" file locally, and a sample
file are provided in the repo.

The three main scripts are:
* `solark_grid_info.py`: returns the current grid frequency and voltages
* `ecobee_mode.py`: sets and gets the current ecobee thermostate mode

Plus there is `ecobee_auth.sh` which is used to authenticate your
application with your Ecobee account.

NOTE: the full solution (to monitor power failures and automatically
set the mode of the ecobee) has not been implemented yet.  So that's
whay you can't find it :)