# FoxESS H3 vs P3 – Szczegółowe porównanie rejestrów Modbus

**Data porównania:** styczeń 2026  
**Źródła:**
- P3: Dokument PDF „FOX commercial inverter Modbus interface definition” (V1.05.03.00, release 2025-01-15)
- H3: Dane z repozytoriów GitHub (nathanmarlor/foxess_modbus, rsaemann/HA-FoxESS-H3-Modbus), wiki społeczności, fora FoxESS Community oraz fragmenty protokołu V1.05.xx (2024–2025)

**Kluczowe wnioski:**
- Rejestry **nie są kompatybilne 1:1** – H3 używa głównie zakresu 31000–32000 (residential/hybrydowy), P3 30000–48000+ (komercyjny/rozbudowany hybrydowy).
- P3 jest znacznie bardziej rozbudowany (do 32 BMS slave, 24 PV strings/MPPT, Meter2, remote control, time periods, fault bitfields, cell voltages).
- H3 prostszy, skupiony na residential (1–2 battery, 2–3 PV, podstawowe EPS/grid phases).
- Gain/skala często różna (np. Voltage: P3 gain 10 → scale 0.1, H3 często 0.1 bezpośrednio).
- Typy: P3 częściej I32/U32 dla mocy/energii, H3 częściej I16/U16.
- RW (zapis): P3 ma dużo więcej (limits, SoC min/max, remote control, time groups). H3 ma mniej (głównie RO).

## 1. Informacje o inwerterze / Model / Wersje

| Sygnał                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres          | H3 Address | H3 Typ / Scale | H3 Opis / Jednostka              | Uwagi / Różnice                              |
|--------------------------------|------------|--------------------|--------------------------------|------------|----------------|----------------------------------|----------------------------------------------|
| Model Name                     | 30000     | STR / - / RO      | 16 rejestrów                   | -          | -              | -                                | Tylko P3 (string)                            |
| Serial Number (SN)             | 30016     | STR / - / RO      | 16 rejestrów                   | -          | -              | -                                | Tylko P3                                     |
| MFG ID                         | 30032     | STR / - / RO      | 16 rejestrów                   | -          | -              | -                                | Tylko P3                                     |
| Master Version                 | 36001     | U16 / - / RO      | -                              | -          | -              | -                                | Tylko P3                                     |
| Slave Version                  | 36002     | U16 / - / RO      | -                              | -          | -              | -                                | Tylko P3                                     |
| Manager Version                | 36003     | U16 / - / RO      | -                              | -          | -              | -                                | Tylko P3                                     |
| Protocol Version               | 39000     | U32 / - / RO      | np. 0x01020304 = v1.2.3.4     | -          | -              | -                                | Tylko P3                                     |
| Inverter State                 | -         | -                 | -                              | 31041     | uint16 / 1     | 1=Self-check, 2=On-grid, 3=EPS...| Tylko H3                                     |
| Temperature Inverter           | -         | -                 | -                              | 31032     | int16 / 0.1    | °C                               | Tylko H3                                     |

## 2. Bateria / BMS

| Sygnał                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres          | H3 Address | H3 Typ / Scale | H3 Opis                          | Uwagi / Różnice                              |
|--------------------------------|------------|--------------------|--------------------------------|------------|----------------|----------------------------------|----------------------------------------------|
| BMS1 Connection Status         | 37002     | U16 / - / RO      | 0=Offline, 1=Online            | -          | -              | -                                | Tylko P3                                     |
| BMS1 Voltage                   | 37609     | U16 / 10 / RO     | V                              | 31034     | int16 / 0.1    | V                                | Różne adresy i gain                          |
| BMS1 Current                   | 37610     | I16 / 10 / RO     | A                              | 31035     | int16 / 0.1    | A (neg=charge)                   | Podobna funkcja, różne typy/gain             |
| BMS1 SoC                       | 37612     | U16 / 1 / RO      | %                              | 31038     | int16 / 1      | %                                | Różne adresy                                 |
| BMS1 SOH                       | 37624     | U16 / 1 / RO      | %                              | -          | -              | -                                | Tylko P3                                     |
| BMS1 Ambient Temp              | 37611     | I16 / 10 / RO     | °C                             | 31037     | int16 / 0.1    | °C (Battery Temp)                | Różne                                     |
| BMS1 Max Cell Voltage          | 37619     | U16 / 1 / RO      | mV                             | -          | -              | -                                | Tylko P3 (szczegółowe komórki)               |
| BMS1 Remain Energy             | 37632     | U16 / 0.1 / RO    | Wh                             | -          | -              | -                                | Tylko P3                                     |
| BMS1 FCC Capacity              | 37633     | U16 / 10 / RO     | Ah                             | -          | -              | -                                | Tylko P3                                     |
| System SoC                     | 39423     | U16 / 1 / RO      | % [0–100]                      | -          | -              | -                                | Tylko P3 (cały system)                       |
| BMS2 Voltage                   | 38307     | U16 / 10 / RO     | V                              | -          | -              | -                                | P3 wspiera drugą baterię                     |
| Battery Power (runtime)        | -         | -                 | -                              | 31036     | int16 / 1      | W (neg=charging)                 | Tylko H3 (runtime)                           |
| Min SoC (RW)                   | 46609     | U16 / 1 / RW      | % [10–100]                     | -          | -              | -                                | Tylko P3 (ustawienia)                        |
| Remote Control (Bitfield)      | 46001     | Bitfield16 / - / RW | -                            | -          | -              | -                                | Tylko P3 (zaawansowana kontrola)             |

## 3. Sieć / Grid / Meter

| Sygnał                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres          | H3 Address | H3 Typ / Scale | H3 Opis                          | Uwagi / Różnice                              |
|--------------------------------|------------|--------------------|--------------------------------|------------|----------------|----------------------------------|----------------------------------------------|
| Meter1 Connection State        | 38801     | U16 / - / RO      | 0=Disconnect, 1=Connect        | -          | -              | -                                | Tylko P3                                     |
| Grid R Phase Voltage           | 38802     | I32 / 10 / RO     | V (2 regs)                     | 31006     | int16 / 0.1    | V Phase R                        | Różne typy (I32 vs I16)                      |
| Grid Combined Active Power     | 38814     | I32 / 10 / RO     | W                              | -          | -              | -                                | P3 ma combined                               |
| Grid Frequency                 | -         | -                 | -                              | 31015     | int16 / 0.01   | Hz Phase R                       | Tylko H3 (w liście)                          |
| Meter2 ...                     | 38901+    | -                 | -                              | -          | -              | -                                | Tylko P3 (drugi meter)                       |

## 4. PV / Strings / MPPT

| Sygnał                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres          | H3 Address | H3 Typ / Scale | H3 Opis                          | Uwagi / Różnice                              |
|--------------------------------|------------|--------------------|--------------------------------|------------|----------------|----------------------------------|----------------------------------------------|
| Number of PV Strings           | 39051     | U16 / 1 / RO      | -                              | -          | -              | -                                | Tylko P3 (do 24)                             |
| PV1 Voltage                    | 39070     | I16 / 10 / RO     | V                              | 31000     | int16 / 0.1    | V                                | Różne gain                                   |
| Total PV Input Power           | 39118     | I32 / ? / RO      | kW (scale 0.001?)              | -          | -              | -                                | Tylko P3 (suma)                              |
| MPPT Voltage (np. MPPT3)       | 39335     | I16 / 10 / RO     | V                              | -          | -              | -                                | P3 do 24 MPPT                                |

## 5. Load / EPS / Inwerter

| Sygnał                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres          | H3 Address | H3 Typ / Scale | H3 Opis                          | Uwagi / Różnice                              |
|--------------------------------|------------|--------------------|--------------------------------|------------|----------------|----------------------------------|----------------------------------------------|
| Inverter Active Power          | 39134     | I32 / ? / RO      | kW                             | -          | -              | -                                | Tylko P3                                     |
| Load Combined Power            | 39225     | I32 / 1 / RO      | W                              | -          | -              | -                                | Tylko P3                                     |
| EPS Combined Power             | 39216     | I32 / 1 / RO      | W                              | -          | -              | -                                | Tylko P3                                     |

## 6. Energie kumulacyjne

| Sygnał                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres          | H3 Address | H3 Typ / Scale | H3 Opis                          | Uwagi / Różnice                              |
|--------------------------------|------------|--------------------|--------------------------------|------------|----------------|----------------------------------|----------------------------------------------|
| Total PV Energy                | 39601     | U32 / 100 / RO    | kWh                            | 32001     | int16 / 0.1    | kWh total                        | Różne zakresy i typy                         |
| Cumulative Generation          | 39149     | U32 / 100 / RO    | kWh                            | -          | -              | -                                | Tylko P3                                     |

**Podsumowanie kompatybilności**  
Integracje dedykowane dla H3 (np. foxess_modbus w HACS) najprawdopodobniej **nie wykryją** P3 automatycznie i nie będą działać bez ręcznej zmiany adresów. Najlepsze rozwiązanie dla P3-10.0-SH to **raw Modbus w Home Assistant** lub własna implementacja w ESPHome.
