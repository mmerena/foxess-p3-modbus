# FoxESS P3 Modbus – Porównanie rejestrów i integracje Home Assistant / ESPHome

<p align="center">
  <img src="https://www.fox-ess.com/wp-content/uploads/2023/05/logo.png" alt="FoxESS Logo" width="300"/>
  <br/>
  <em>Integracja Modbus dla inwerterów FoxESS P3 (komercyjne hybrydowe) – pełna analiza rejestrów vs H3</em>
</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/mmerena/foxess-p3-modbus?style=social)](https://github.com/mmerena/foxess-p3-modbus)
[![GitHub issues](https://img.shields.io/github/issues/mmerena/foxess-p3-modbus)](https://github.com/mmerena/foxess-p3-modbus/issues)

## O projekcie

Projekt ma na celu zebranie i porównanie **pełnych rejestrów Modbus** dla inwerterów FoxESS serii **P3** (np. P3-10.0-SH) w porównaniu do serii **H3** (residential).

Źródła:
- Oficjalny dokument FoxESS „Commercial Inverter Modbus Interface Definition” V1.05.03.00 (2025-01-15)
- Społecznościowe mapy rejestrów H3 z repozytoriów GitHub (nathanmarlor/foxess_modbus, rsaemann/HA-FoxESS-H3-Modbus, TonyM1958/HA-FoxESS-Modbus)

**Dlaczego warto?**
- Integracje H3 (np. foxess_modbus w HACS) **nie wykrywają** P3 automatycznie
- P3 ma zupełnie inne adresy, gain, typy i znacznie więcej rejestrów (multi-BMS, 24 PV/MPPT, remote control, time periods, cell voltages, faults bitfields)
- Projekt dostarcza gotowe konfiguracje dla **Home Assistant** (raw Modbus) i **ESPHome** + szczegółowe porównanie tabelaryczne

## Zawartość repozytorium
.
├── README.md                     ← ten plik
├── COMPARISON.md                 ← maksymalnie rozbudowane porównanie H3 vs P3 (wszystkie rejestry z PDF)
├── ha/
│   └── configuration.yaml        ← przykładowa konfiguracja Modbus w Home Assistant (slave 247)
├── esphome/
│   └── foxess-p3.yaml            ← konfiguracja ESPHome jako most Modbus TCP → HA API
├── scripts/
│   └── test_modbus.py            ← prosty skrypt Python (pymodbus) do testów rejestrów
└── docs/
└── FoxESS Modbus Protocol--20250115 (V1.05.03.00).pdf  ← oryginalny dokument PDF


## Porównanie H3 vs P3 – kluczowe różnice

| Cecha                          | P3 (komercyjne)                          | H3 (residential)                        | Uwagi / Kompatybilność |
|-------------------------------|------------------------------------------|-----------------------------------------|------------------------|
| Zakres adresów                | 30000–49210+                             | 31000–32000+, 41000–49200+             | Brak wspólnych bloków  |
| Liczba BMS                    | Do 2 BMS × 32 slave                      | 1 BMS                                   | P3 znacznie bardziej rozbudowany |
| PV Strings / MPPT             | Do 24                                    | 2–3                                     | P3 komercyjny zakres   |
| Meter/CT                      | 2× Meter (Meter1 + Meter2)               | 1× Smart Meter                          | P3 ma fazy reactive/apparent/PF |
| Fault / Alarm                 | 3× Alarm + 6× Fault bitfield per BMS     | Podstawowe statusy                      | P3 szczegółowe bitfields |
| RW – kontrola                 | Remote Control, time periods (do 24), limits, SoC min/max | Charge periods (1–2), SoC limits        | P3 ma zaawansowany remote |
| Kompatybilność integracji H3  | Nie działa bez remapowania               | Działa natywnie (foxess_modbus HACS)    | → Użyj raw Modbus dla P3 |

Pełne porównanie → [COMPARISON.md](COMPARISON.md)

## Jak zacząć – Home Assistant (raw Modbus)

1. Dodaj do `configuration.yaml`:

```yaml
modbus:
  - name: foxess_p3
    type: tcp
    host: 192.168.1.10
    port: 502
    timeout: 5
    slave: 247

    sensors:
      - name: FoxESS Model Name
        address: 30000
        data_type: string
        count: 16
        scan_interval: 300

      - name: BMS1 SoC
        address: 37612
        data_type: uint16
        unit_of_measurement: "%"
        precision: 0
        scan_interval: 10

      - name: Grid Combined Active Power
        address: 38814
        data_type: int32
        scale: 0.1
        unit_of_measurement: W
        precision: 1
        scan_interval: 5

      # Dodaj więcej z COMPARISON.md
```

2. Restart HA → sprawdź encje w Ustawienia → Urządzenia i usługi.

Pełna konfiguracja → ha/configuration.yaml

## Jak zacząć – ESPHome (most Modbus → HA)

```yaml
modbus_controller:
  - id: foxess_p3
    address: 247
    modbus_id: modbus_fox

sensor:
  - platform: modbus_controller
    modbus_controller_id: foxess_p3
    name: "BMS1 SoC"
    register_type: holding
    address: 37612
    value_type: U_WORD
    unit_of_measurement: "%"
    update_interval: 10s

  - platform: modbus_controller
    modbus_controller_id: foxess_p3
    name: "PV Total Power"
    register_type: holding
    address: 39118
    value_type: S_DWORD
    filters:
      - multiply: 0.001
    unit_of_measurement: kW
    update_interval: 10s
```

Pełna konfiguracja → esphome/foxess-p3.yaml

## Testowanie rejestrów (Python + pymodbus)

```python
# scripts/test_modbus.py
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.10', port=502)
client.connect()

# Czytaj model (string, 16 regs)
result = client.read_holding_registers(30000, 16, slave=247)
if not result.isError():
    model = ''.join(chr(x >> 8) + chr(x & 0xFF) for x in result.registers).strip('\x00')
    print("Model:", model)

client.close()
```
Uruchom: python scripts/test_modbus.py

## Licencja

MIT License – szczegóły w pliku LICENSE

## Contributing

1. Fork repozytorium
2. Stwórz branch (git checkout -b feature/nazwa-funkcji)
3. Commit zmian (git commit -m 'Dodano rejestr XYZ')
4. Push (git push origin feature/nazwa-funkcji)
5. Otwórz Pull Request

Mile widziane:

- Nowe testy rejestrów (mbpoll / pymodbus)
- Poprawki gain/typów
- Dodatkowe YAML dla ESPHome / Node-RED
- Zgłoszenia błędów z Twojego P3-10.0-SH

Dziękuję za każdą pomoc! 🚀

© 2026 – projekt społecznościowy, nieoficjalny. FoxESS® to znak towarowy FoxESS Co., Ltd.


