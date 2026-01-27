# Heat Demand - Home Assistant Custom Integration

Calculates the maximum heat demand across all selected radiators/thermostats by comparing target vs current temperatures.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the menu (⋮) → **Custom repositories**
3. Add `https://github.com/rawnsley/CompCurve` as an **Integration**
4. Search for "Heat Demand" and install
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/heat_demand` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Heat Demand"
3. Select the climate entities (radiators/thermostats) to monitor

## How It Works

For each selected climate entity, the integration:

1. Reads the `temperature` attribute (target temperature)
2. Reads the `current_temperature` attribute
3. Calculates the difference: `target - current`
4. Finds the maximum difference across all entities
5. Subtracts the **Overshoot Threshold** (default: 1°C) to prevent overshoot
6. Returns the result, clipped to never fall below zero

### Overshoot Threshold

The overshoot threshold is subtracted from the calculated heat demand to prevent temperature overshoot. For example, if the maximum demand is 2.5°C and the threshold is 1°C, the reported demand will be 1.5°C. This causes the heating system to reduce output as the room approaches the target temperature, preventing overshoot.

## Output

The integration creates a sensor with:

- **State**: Maximum heat demand in °C (always ≥ 0)
- **Attributes**:
  - `climate_entities`: List of monitored entities
  - `individual_demands`: Dictionary showing each entity's demand (can be negative if room is too warm)

## Use with CompCurve

This integration is designed to work with the Compensation Curve integration:

1. Install both Heat Demand and Compensation Curve integrations
2. Configure Heat Demand with your radiator climate entities
3. In Compensation Curve configuration, select the Heat Demand sensor as the "Heat Demand Sensor"
4. Adjust the Heat Demand Coefficient as needed (default: 1.0)

This creates a feedback loop where rooms that are far below their target temperature will increase the boiler flow temperature.
