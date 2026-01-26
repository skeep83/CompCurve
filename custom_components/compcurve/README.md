# Compensation Curve - Home Assistant Custom Integration

Weather-compensated heating flow temperature calculator for Home Assistant.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the menu (⋮) → **Custom repositories**
3. Add `https://github.com/rawnsley/CompCurve` as an **Integration**
4. Search for "Compensation Curve" and install
5. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/compcurve` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "Compensation Curve"
3. Select your sensors:
   - **Outdoor Temperature**: Required
   - **Wind Speed**: Optional (enables wind compensation)
   - **Sunlight/Irradiance**: Optional (enables solar compensation)
   - **Heat Demand**: Optional (enables heat demand compensation - use with the Heat Demand integration)

## Adjusting Parameters

After setup, all parameters are available as number entities on the device page:

1. Go to **Settings** → **Devices & Services**
2. Find "Compensation Curve" and click the device
3. Adjust parameters directly using the sliders in the Configuration section

To change sensors, click **Configure** on the integration.

## Formula

```
TFlow = scale × (HC × max(0, Tbase - Tout))^exp + Tbase + wind_coef × wind^wind_exp - solar_coef × sun + demand_coef × demand
```

Default values:
- Scale factor: 2.5
- Exponent: 0.8
- Heat curve (HC): 0.75
- Wind coefficient: 0.25
- Wind exponent: 0.9
- Solar coefficient: 0.1
- Heat demand coefficient: 1.0

See the main [README](../../README.md) for detailed formula documentation.

## Lovelace Dashboard

Pre-built dashboard cards are available in the [lovelace](../../lovelace/) folder:

- **dashboard.yaml** - Complete multi-tab dashboard
- **dashboard-single.yaml** - Single-page dashboard with sections

See [lovelace/README.md](../../lovelace/README.md) for installation instructions.
