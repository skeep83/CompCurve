# CompCurve

Temperature compensation curve equation for home heating system with Home Assistant integration.

## Installation Options

### Custom Integration (Recommended)

Install via HACS for a UI-configurable sensor with adjustable coefficients:

1. Add this repo as a custom repository in HACS
2. Install "Compensation Curve"
3. Configure via **Settings** → **Devices & Services** → **Add Integration**

See [custom_components/compcurve/](custom_components/compcurve/) for details.

### Template Sensor

For a simple template sensor without UI configuration, use the formula below.

## Home Assistant Template Equation

```python
{{ min(60, max(20,
    2.5 * (0.75 * max(0, 20 - float(states('sensor.gw3000a_outdoor_temperature')))) ** 0.8 + 20
    + 0.25 * float(states('sensor.average_wind_speed_hourly')) ** 0.9
    - 0.1 * float(states('sensor.average_sunlight_hourly'), 0)
)) }}
```

## What is a Compensation Curve?

A compensation curve (also known as a weather compensation curve) automatically adjusts your heating system's flow temperature based on outdoor temperature. This ensures:

- Optimal comfort levels
- Energy efficiency
- Reduced heating costs
- Consistent indoor temperatures

### How It Works

- **Lower outdoor temperatures** → Higher heating flow temperatures
- **Higher outdoor temperatures** → Lower heating flow temperatures

## Formula Breakdown

**Base Formula:**
`TFlow = 2.5 × (HC × (Tset - Tout))^0.8 + Tset + WindAdjustment - SolarAdjustment`

### Components

1. **Non-linear base calculation**: `2.5 × (HC × (Tset - Tout))^0.8 + Tset`
   - **HC** = Heat Curve parameter = 0.75 (adjustable 0.5-1.5)
   - **Tset** = Set/comfort temperature = 20°C
   - **0.8** = Exponent matching radiator physics
   - **2.5** = Scaling constant from Vaillant heat pump analysis
   - Creates a curved response that matches how radiators actually transfer heat

2. **Wind chill compensation**: `+ 0.25 × wind_speed^0.9`
   - Adds extra heating when windy (wind increases heat loss)
   - Power law provides gradual increase with diminishing returns
   - Typically adds 0-5°C depending on conditions (see graph below)

3. **Solar gain compensation**: `- 0.1 × sunlight`
   - Reduces heating when sun is shining (solar gain heats the house passively)
   - Linear relationship: heat input is proportional to solar irradiance
   - Sunlight measured in W/m² (from `sensor.average_sunlight_hourly`)
   - Tuned for -10°C at 100 W/m² (see table below)

4. **Safety limits**: `min(60, max(20, ...))`
   - **Minimum**: 20°C (prevents system shutdown)
   - **Maximum**: 60°C (protects components and prevents scalding)

5. **Default value handling**: `float(states('sensor...'), 0)` → returns 0 if sensor unavailable

## Why Non-Linear?

Radiator heat output is non-linear due to two heat transfer mechanisms:
- **Radiation**: Linear relationship to temperature difference
- **Convection**: Non-linear due to variable air flow speeds (chimney effect)

The 0.8 exponent compensates for this physics, ensuring heating power remains proportional to the actual heating need across all conditions.

## Compensation Curve Visualization

![Compensation Curve](compensation-curve.svg)

The graph shows the non-linear relationship between outdoor and flow temperatures for three different Heat Curve (HC) parameter values:

- **HC = 0.5 (Conservative)**: Milder heating, lower flow temperatures
- **HC = 0.75 (Default)**: Recommended balance for most systems
- **HC = 1.0 (Aggressive)**: Higher flow temperatures, more intense heating

Notice all curves are steeper at lower temperatures (more aggressive heating when cold) and flatten as they approach indoor comfort levels. The HC parameter shifts the entire curve up or down without changing its fundamental shape.

## Wind Adjustment Visualization

![Wind Adjustment](wind-adjustment.svg)

The wind adjustment follows a power law curve, providing compensation that increases gradually with wind speed, matching real-world observations of wind-induced heat loss.

## Solar Gain Adjustment

| Sunlight (W/m²) | Condition      | Adjustment |
|-----------------|----------------|------------|
| 0               | Night/Dark     | 0.0°C      |
| 25              | Dawn/Dusk      | -2.5°C     |
| 50              | Heavy overcast | -5.0°C     |
| 100             | Overcast       | -10.0°C    |
| 200             | Light clouds   | -20.0°C    |
| 500             | Partly sunny   | -50.0°C    |
| 1000            | Peak sun       | -100.0°C   |

The solar gain uses a linear relationship (`-0.1 × sunlight`) tuned for -10°C at 100 W/m². At higher sunlight levels, the safety minimum of 20°C prevents excessive reduction. This aggressive compensation reflects significant passive heating through windows.

## Temperature Reference Table (HC = 0.75)

| Outdoor Temp | Flow Temp (no wind) | 10 km/h wind | 20 km/h wind | 30 km/h wind |
|--------------|---------------------|--------------|--------------|--------------|
| -20°C        | 58.0°C              | 60.0°C       | 60.0°C       | 60.0°C       |
| -10°C        | 50.2°C              | 52.2°C       | 53.9°C       | 55.5°C       |
| -5°C         | 46.1°C              | 48.1°C       | 49.8°C       | 51.4°C       |
| 0°C          | 41.8°C              | 43.8°C       | 45.5°C       | 47.2°C       |
| 5°C          | 37.3°C              | 39.3°C       | 41.0°C       | 42.7°C       |
| 10°C         | 32.5°C              | 34.5°C       | 36.2°C       | 37.9°C       |
| 15°C         | 27.2°C              | 29.2°C       | 30.9°C       | 32.5°C       |
| 20°C         | 20.0°C (min)        | 22.0°C       | 23.7°C       | 25.3°C       |

![Table Graph](table-graph.svg)

The graph visualizes all values from the table above, showing how flow temperature varies with outdoor temperature across four wind scenarios. Notice how the curves are parallel, with wind adding a consistent offset across all outdoor temperatures.

## Reference

Formula based on Vaillant heat pump compensation curve analysis:<br>
[Vaillant Heat Pump Controls: The Heat Curves](https://protonsforbreakfast.wordpress.com/2024/10/16/vaillant-heat-pump-controls-part-1-the-heat-curves/)

## Previous Linear Version

The original linear formula (`48 - outdoor_temp`) has been replaced with this non-linear version for better efficiency and radiator physics matching. See git history for the previous implementation.
