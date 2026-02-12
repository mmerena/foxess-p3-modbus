
```text
/config
 ├── configuration.yaml
 └── packages/
      ├── foxess/
      │     ├── 00_modbus.yaml
      │     ├── 10_sensors_modbus.yaml
      │     ├── 20_templates.yaml
      │     ├── 30_helpers.yaml
      │     ├── 40_switches.yaml
      │     ├── 50_scripts.yaml
      │     ├── 60_automations.yaml
      │     └── 90_debug.yaml
```

configuration.yaml
```yaml
homeassistant:
  packages: !include_dir_merge_named packages/foxess
```

00_modbus.yaml
```yaml
modbus:
  - name: foxess_modbus
    type: tcp
    host: 192.168.1.100
    port: 502
    timeout: 5
    message_wait_milliseconds: 30
```

10_sensors_modbus.yaml
```yaml
modbus:
  - name: foxess_modbus
    sensors:

      - name: FoxESS 30000 Model Name
        unique_id: foxess_30000_model_name
        slave: 247
        address: 30000
        data_type: string
        count: 16
        scan_interval: 3600

      - name: FoxESS 46001 Remote Control Raw
        unique_id: foxess_46001_remote_control_raw
        slave: 247
        address: 46001
        input_type: holding
        data_type: uint16
        scan_interval: 30

      - name: FoxESS 49203 Work Mode Raw
        unique_id: foxess_49203_work_mode_raw
        slave: 247
        address: 49203
        input_type: holding
        data_type: uint16
        scan_interval: 30
```

20_templates.yaml
```yaml
template:

  - sensor:
      - name: FoxESS Remote Enable Bit
        state: >
          {{ states('sensor.foxess_46001_remote_control_raw') | int(0) % 2 }}

  - binary_sensor:
      - name: FoxESS Remote Enabled
        state: >
          {{ (states('sensor.foxess_46001_remote_control_raw') | int(0)) % 2 == 1 }}

  - select:
      - name: FoxESS 49203 Work Mode
        state: >
          {% set v = states('sensor.foxess_49203_work_mode_raw') | int(0) %}
          {% if v == 6 %}Force Charge{% elif v == 7 %}Force Discharge{% else %}Other{% endif %}
        options:
          - Other
          - Force Charge
          - Force Discharge
```

30_helpers.yaml
```yaml
input_select:
  foxess_46001_controlled_target:
    name: FoxESS 46001 Controlled Target
    options:
      - AC
      - Battery
      - Grid
      - AC Grid First

  foxess_46001_power_direction:
    name: FoxESS 46001 Power Direction
    options:
      - Generation
      - Consumption

input_number:
  foxess_46001_last_written:
    name: FoxESS 46001 Last Written
    min: 0
    max: 65535
    step: 1

  foxess_46001_last_write_ts:
    name: FoxESS 46001 Last Write Timestamp
    min: 0
    max: 9999999999
    step: 1
```

40_switches.yaml
```yaml
switch:
  - platform: template
    switches:

      foxess_46001_remote_enable:
        value_template: >
          {{ (states('sensor.foxess_46001_remote_control_raw') | int(0)) % 2 == 1 }}
        turn_on:
          service: script.foxess_46001_write_safe
        turn_off:
          service: script.foxess_46001_write_safe
```

50_scripts.yaml
```yaml
```

60_automations.yaml
```yaml
```

70_g13_logic.yaml

80_ems_controller.yaml

90_debug.yaml
```yaml
template:
  - sensor:
      - name: FoxESS Remote Bitfield Decoded
        state: >
          {{ states('sensor.foxess_46001_remote_control_raw') }}
```
