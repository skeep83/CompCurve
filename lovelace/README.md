# CompCurve Lovelace Dashboard

This folder contains Lovelace card configurations for visualizing and controlling the CompCurve integration.

## Installation

### Option 1: Complete Dashboard (Recommended)

1. In Home Assistant, go to **Settings** → **Dashboards**
2. Click **Add Dashboard** → **New dashboard from scratch**
3. Name it "Compensation Curve" and click **Create**
4. Click the three dots menu → **Edit Dashboard**
5. Click the three dots menu → **Raw configuration editor**
6. Replace the contents with the content from `dashboard.yaml`
7. Click **Save**

## Entity Naming

The cards use entity IDs based on the default naming pattern:
- `sensor.compensation_curve_target_flow_temperature`
- `sensor.compensation_curve_compensated_flow_temperature`
- `number.compensation_curve_heat_curve`
- etc.

If your entities have different names (e.g., you renamed the integration), you'll need to update the entity IDs in the YAML files.

## Prerequisites

These cards use standard Home Assistant card types and require no additional custom cards. However, for the best experience, you may want to install:

- **ApexCharts Card** (via HACS) - For more advanced charting options
- **mini-graph-card** (via HACS) - Alternative compact graph style

## Screenshots

(Add screenshots of your dashboard here)
