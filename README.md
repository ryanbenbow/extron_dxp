# Extron DXP Matrix Integration

Control Extron DXP Matrix Switchers via Home Assistant.

## Features
- **Config Flow:** Setup via UI.
- **Select Entities:** Controls for Outputs 1-8.
- **Service:** `extron_dxp.set_all_outputs` to route one input to all screens.

## Installation
1. Install via HACS (Custom Repositories > `ryanbenbow/extron_dxp`).
2. Add Integration in Settings > Devices & Services.

## Dashboard Card Configuration
To get the custom Matrix Interface, you need the **card-mod** frontend integration installed from HACS.

**1. Create a Helper:**
Go to Settings > Devices > Helpers > Create Helper > **Dropdown**.
- Name: `Extron Input Select`
- Options: `1`, `2`, `3` ... up to `16`.

**2. Add this Manual Card:**
```yaml
type: vertical-stack
cards:
  # --- 1. INPUTS ---
  - type: grid
    columns: 8
    square: true
    title: 1. Select Input Source
    cards:
      {% for i in range(1, 17) %}
      - type: button
        name: "{{ i }}"
        tap_action: {action: call-service, service: input_select.select_option, service_data: {entity_id: input_select.extron_input_select, option: "{{ i }}"}}
        card_mod: {style: "ha-card { background: {% if is_state('input_select.extron_input_select', '{{ i }}') %} #00D700 {% else %} #333 {% endif %} !important; color: {% if is_state('input_select.extron_input_select', '{{ i }}') %} black {% else %} white {% endif %} !important; border: 1px solid #555; }"}
      {% endfor %}

  # --- 2. OUTPUTS ---
  - type: grid
    columns: 4
    square: true
    title: 2. Select Destinations
    cards:
      {% for i in range(1, 9) %}
      - type: button
        entity: select.extron_output_{{ i }}
        show_name: false
        show_icon: false
        tap_action:
          action: call-service
          service: select.select_option
          target: {entity_id: select.extron_output_{{ i }}}
          data: {option: "{{ states('input_select.extron_input_select') }}"}
        card_mod:
          style: |
            ha-card {
              background: #222 !important;
              border: 2px solid {% if states('select.extron_output_{{ i }}') == states('input_select.extron_input_select') %} #00ff00 {% else %} #444 {% endif %} !important;
              position: relative !important;
            }
            ha-card::before {
              content: "OUT {{ i }}";
              position: absolute; top: 15%; left: 0; right: 0; font-size: 14px; font-weight: bold; color: #fff; text-align: center;
            }
            ha-card::after {
              content: "IN " attr(data-state);
              /* We simulate state via Jinja because CSS can't read attributes directly easily in simple mod */
              content: "IN {{ states('select.extron_output_{{ i }}') }}";
              position: absolute; bottom: 20%; left: 0; right: 0; font-size: 12px; color: #ccc; text-align: center;
            }
      {% endfor %}

  # --- 3. CONTROLS ---
  - type: grid
    columns: 2
    cards:
      - type: button
        name: "ROUTE TO ALL"
        icon: mdi:arrow-expand-all
        tap_action:
          action: call-service
          service: extron_dxp.set_all_outputs
          data:
            input: "{{ states('input_select.extron_input_select') | int }}"
        card_mod: {style: "ha-card { background: #E65100 !important; color: white !important; font-weight: bold; }"}
        
      - type: button
        name: "RELEASE ALL"
        icon: mdi:cancel
        tap_action:
          action: call-service
          service: extron_dxp.set_all_outputs
          data: {input: 0}
        card_mod: {style: "ha-card { background: #8B0000 !important; color: white !important; font-weight: bold; }"}
