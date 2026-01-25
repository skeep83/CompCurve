"""Constants for the Compensation Curve integration."""

DOMAIN = "compcurve"

# Configuration keys
CONF_OUTDOOR_TEMP_SENSOR = "outdoor_temp_sensor"
CONF_WIND_SPEED_SENSOR = "wind_speed_sensor"
CONF_SUNLIGHT_SENSOR = "sunlight_sensor"
CONF_HEAT_CURVE = "heat_curve"
CONF_BASE_TEMP = "base_temp"
CONF_MIN_FLOW_TEMP = "min_flow_temp"
CONF_MAX_FLOW_TEMP = "max_flow_temp"
CONF_SCALE_FACTOR = "scale_factor"
CONF_EXPONENT = "exponent"
CONF_WIND_COEFFICIENT = "wind_coefficient"
CONF_WIND_EXPONENT = "wind_exponent"
CONF_SOLAR_COEFFICIENT = "solar_coefficient"

# Default values
DEFAULT_HEAT_CURVE = 0.75
DEFAULT_BASE_TEMP = 20.0
DEFAULT_MIN_FLOW_TEMP = 20.0
DEFAULT_MAX_FLOW_TEMP = 60.0
DEFAULT_SCALE_FACTOR = 2.5
DEFAULT_EXPONENT = 0.8
DEFAULT_WIND_COEFFICIENT = 0.25
DEFAULT_WIND_EXPONENT = 0.9
DEFAULT_SOLAR_COEFFICIENT = 0.1
