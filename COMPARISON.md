# FoxESS H3 vs P3 – Porównanie rejestrów Modbus

**Wersja dokumentu:** 2.0 – pełna ekstrakcja z PDF P3 + społecznościowe H3  
**Data aktualizacji:** 30 stycznia 2026  
**Autor:** [mmerena] – analiza na podstawie PDF V1.05.03.00 (2025-01-15) i repo GitHub  
**Licencja:** MIT – kopiuj, modyfikuj, używaj w projektach open-source

## Wstęp i kluczowe wnioski

**P3** (komercyjne hybrydowe, np. P3-10.0-SH):  
- Pełna lista z PDF – ~391 rejestrów (model, wersje, 2×BMS z 32 slave, 2×Meter/CT, do 24 PV/MPPT/strings, runtime grid/inv/load/EPS/battery, energie, RW remote control/time periods/limits/faults).  
- Slave ID: 247 (domyślny).  
- Gain/skala: często 10 dla V/A/°C, 100 dla A (PV), 0.1 dla Wh.  
- Typy: dużo I32/U32 dla mocy/energii (2 rejestry), bitfield dla fault/alarm.  
- RW: zaawansowane (remote, limits, SoC min/max, time groups do 24, battery currents).

**H3** (residential hybrydowe, np. H3-10.0 / H3 Smart / H3 Pro):  
- Społecznościowe mapy (GitHub rsaemann, nathanmarlor/foxess_modbus, TonyM1958, StealthChesnut) – ~150–200 rejestrów.  
- Zakresy: 31000–31051 (runtime PV/grid/battery/EPS), 32000–32043 (energies), 41000–41024 (charge periods), 44000+ (settings), 49200+ (idle/power limits).  
- Slave ID: 1 lub 247 (zależnie od firmware).  
- Gain/skala: często 0.1 dla V/A/°C/W, 0.01 dla Hz.  
- RW: podstawowe (charge periods 1–2, SoC limits, enable/disable).

**Kompatybilność:** ~0% – adresy, gain, typy, zakresy całkowicie różne. Integracje H3 nie działają z P3 bez remapowania.  
**Rekomendacja dla P3:** Raw Modbus w HA (slave 247) lub custom Python/ESPHome.  
**Testy:** Użyj mbpoll -m tcp -a 247 -r XXXX -t 3/4 192.168.1.10 do weryfikacji.

## 1. Informacje o modelu, wersjach, meterach

| Nr | Sygnał name                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres / Opis                  | H3 Address | H3 Typ / Scale / RW | H3 Jednostka / Opis                  | Uwagi / Różnice / Test notes                         |
|----|--------------------------------------|------------|--------------------|-----------------------------------------------|------------|---------------------|--------------------------------------|------------------------------------------------------|
| 1  | Model name                           | 30000     | STR / N/A / RO    | 16 regs (32 chars)                            | -          | -                   | -                                    | Tylko P3; H3 brak string.                            |
| 2  | SN                                   | 30016     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
| 3  | MFG ID                               | 30032     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
| 4  | Master Version                       | 36001     | U16 / N/A / RO    | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
| 5  | Slave Version                        | 36002     | U16 / N/A / RO    | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
| 6  | Manager Version                      | 36003     | U16 / N/A / RO    | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
| 7  | Meter1 SN                            | 36100     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3 (multi-meter).                              |
| 8  | Meter1 MFG ID                        | 36116     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
| 9  | Meter1 TYPE                          | 36132     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|10  | Meter1 Version                       | 36148     | STR / N/A / RO    | 1 reg                                         | -          | -                   | -                                    | Tylko P3.                                            |
|11  | Meter2 SN                            | 36200     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|12  | Meter2 MFG ID                        | 36216     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|13  | Meter2 TYPE                          | 36232     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|14  | Meter2 Version                       | 36248     | STR / N/A / RO    | 1 reg                                         | -          | -                   | -                                    | Tylko P3.                                            |
|   | Protocol Version                     | 39000     | U32 / N/A / RO    | np. 0x01020304 = v1.2.3.4                    | -          | -                   | -                                    | Tylko P3.                                            |
|   | Model Name (runtime)                 | 39002     | STR / 1 / RO      | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|   | SN (runtime)                         | 39018     | STR / 1 / RO      | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|   | PN                                   | 39034     | STR / 1 / RO      | 16 regs                                       | -          | -                   | -                                    | Tylko P3 (Part Number).                              |
|   | Model ID                             | 39050     | U16 / 1 / RO      | -                                             | -          | -                   | -                                    | Tylko P3.                                            |

### 2. BMS / Battery (pełna lista z PDF)

| Nr | Sygnał name                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres / Opis                  | H3 Address | H3 Typ / Scale / RW | H3 Jednostka / Opis                  | Uwagi / Różnice                                      |
|----|--------------------------------------|------------|--------------------|-----------------------------------------------|------------|---------------------|--------------------------------------|------------------------------------------------------|
|15 | BMS1 Connection Status               | 37002     | U16 / N/A / RO    | 0=Offline, 1=Online                           | -          | -                   | -                                    | Tylko P3 (multi-BMS).                                |
|16 | BMS1 Master Version                  | 37003     | U16 / N/A / RO    | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
|17 | BMS1 Master Type                     | 37004     | U16 / N/A / RO    | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
|18 | BMS1 Master SN                       | 37005     | STR / N/A / RO    | 16 regs                                       | -          | -                   | -                                    | Tylko P3.                                            |
|19 | BMS1 Slave Number                    | 37032     | U16 / 1 / RO      | [0-32], 0 invalid                             | -          | -                   | -                                    | Tylko P3 (do 32 slave).                              |
|20 | BMS1 Slave 1 Version                 | 37033     | U16 / N/A / RO    | Per slave: 37033+(n-1)                        | -          | -                   | -                                    | Tylko P3.                                            |
|21 | BMS1 Slave 2 Version                 | 37034     | U16 / N/A / RO    | ...                                           | -          | -                   | -                                    | Tylko P3.                                            |
|22 | BMS1 Slave1 SN                       | 37097     | STR / N/A / RO    | Per slave: 37097+16*(n-1)                     | -          | -                   | -                                    | Tylko P3.                                            |
|23 | BMS1 Slave2 SN                       | 37113     | STR / N/A / RO    | ...                                           | -          | -                   | -                                    | Tylko P3.                                            |
|24 | BMS1 Voltage                         | 37609     | U16 / 10 / RO     | V                                             | 31034     | int16 / 0.1 / RO    | V                                    | Różne gain (P3 scale 0.1).                           |
|25 | BMS1 Current                         | 37610     | I16 / 10 / RO     | A                                             | 31035     | int16 / 0.1 / RO    | A (neg=charge)                       | Różne gain.                                          |
|26 | BMS1 Ambient Temperature             | 37611     | I16 / 10 / RO     | °C                                            | -          | -                   | -                                    | Tylko P3.                                            |
|27 | BMS1 SoC                             | 37612     | U16 / 1 / RO      | %                                             | 31038     | int16 / 1 / RO      | %                                    | Różne adresy.                                        |
|28 | BMS1 Max Temperature                 | 37617     | I16 / 10 / RO     | °C                                            | -          | -                   | -                                    | Tylko P3.                                            |
|29 | BMS1 Min Temperature                 | 37618     | I16 / 10 / RO     | °C                                            | -          | -                   | -                                    | Tylko P3.                                            |
|30 | BMS1 Max Cell Voltage                | 37619     | U16 / 1 / RO      | mV                                            | -          | -                   | -                                    | Tylko P3.                                            |
|31 | BMS1 Min Cell Voltage                | 37620     | U16 / 1 / RO      | mV                                            | -          | -                   | -                                    | Tylko P3.                                            |
|32 | BMS1 SOH                             | 37624     | U16 / 1 / RO      | %                                             | -          | -                   | -                                    | Tylko P3.                                            |
|33 | BMS1 Fault1                          | 37626     | Bitfield16 / RO   | Bitfield                                      | -          | -                   | -                                    | Tylko P3 (6 fault bitfields).                        |
|34 | BMS1 Fault2                          | 37627     | Bitfield16 / RO   | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|35 | BMS1 Fault3                          | 37628     | Bitfield16 / RO   | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|36 | BMS1 Fault4                          | 37629     | Bitfield16 / RO   | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|37 | BMS1 Fault5                          | 37630     | Bitfield16 / RO   | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|38 | BMS1 Fault6                          | 37631     | Bitfield16 / RO   | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|39 | BMS1 Remain Energy                   | 37632     | U16 / 0.1 / RO    | Wh                                            | -          | -                   | -                                    | Tylko P3.                                            |
|40 | BMS1 FCC Capacity                    | 37633     | U16 / 10 / RO     | Ah                                            | -          | -                   | -                                    | Tylko P3.                                            |
|41 | reserve                              | 37634     | U16 / N/A / RO    | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
|42 | BMS1 Design Energy                   | 37635     | U16 / 0.1 / RO    | Wh                                            | -          | -                   | -                                    | Tylko P3.                                            |
|43 | BMS1 Force to Change battery Flag    | 37636     | U16 / N/A / RO    | 0=Reset, 1=Set (charge)                       | -          | -                   | -                                    | Tylko P3.                                            |
|44 | BMS2 Connection Status               | 37700     | U16 / N/A / RO    | 0=Offline, 1=Online                           | -          | -                   | -                                    | Tylko P3.                                            |
|...| ... (BMS2 analogicznie do BMS1)      | 37701–38334 | ...              | ...                                           | -          | -                   | -                                    | P3 wspiera BMS2.                                     |

### 3. Meter / CT / Grid phases (pełna lista z PDF)

| Nr | Sygnał name                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres / Opis                  | H3 Address | H3 Typ / Scale / RW | H3 Jednostka / Opis                  | Uwagi / Różnice                                      |
|----|--------------------------------------|------------|--------------------|-----------------------------------------------|------------|---------------------|--------------------------------------|------------------------------------------------------|
|73 | Meter1/CT1 Connection State          | 38801     | U16 / N/A / RO    | 0=Disconnect, 1=Connect                       | -          | -                   | -                                    | Tylko P3.                                            |
|74 | Meter1/CT1 R Phase Voltage           | 38802     | I32 / 10 / RO     | V (2 regs)                                    | 31006     | int16 / 0.1 / RO    | V Phase R                            | P3 I32, H3 I16.                                      |
|75 | Meter1/CT1 S Phase Voltage           | 38804     | I32 / 10 / RO     | V                                             | 31007     | int16 / 0.1 / RO    | V Phase S                            | Podobnie.                                            |
|76 | Meter1/CT1 T Phase Voltage           | 38806     | I32 / 10 / RO     | V                                             | 31008     | int16 / 0.1 / RO    | V Phase T                            | Podobnie.                                            |
|77 | Meter1/CT1 R Phase Current           | 38808     | I32 / 1000 / RO   | A                                             | 31009     | int16 / 0.1 / RO    | A Phase R                            | P3 0.001 A.                                          |
|78 | Meter1/CT1 S Phase Current           | 38810     | I32 / 1000 / RO   | A                                             | 31010     | int16 / 0.1 / RO    | A Phase S                            | Podobnie.                                            |
|79 | Meter1/CT1 T Phase Current           | 38812     | I32 / 1000 / RO   | A                                             | 31011     | int16 / 0.1 / RO    | A Phase T                            | Podobnie.                                            |
|80 | Meter1/CT1 Combined Active Power     | 38814     | I32 / 10 / RO     | W                                             | -          | -                   | -                                    | Tylko P3 (combined).                                 |
|81 | Meter1/CT1 R Phase Active Power      | 38816     | I32 / 10 / RO     | W                                             | 31012     | int16 / 1 / RO      | W Phase R                            | H3 I16.                                              |
|82 | Meter1/CT1 S Phase Active Power      | 38818     | I32 / 10 / RO     | W                                             | 31013     | int16 / 1 / RO      | W Phase S                            | Podobnie.                                            |
|83 | Meter1/CT1 T Phase Active Power      | 38820     | I32 / 10 / RO     | W                                             | 31014     | int16 / 1 / RO      | W Phase T                            | Podobnie.                                            |
|   | Meter1/CT1 Combined Reactive Power   | 38822     | I32 / 10 / RO     | var                                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | Meter1/CT1 R Phase Reactive Power    | 38824     | I32 / 10 / RO     | var                                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | ... (S/T Reactive)                   | 38826/28  | I32 / 10 / RO     | var                                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | Meter1/CT1 Combined Apparent Power   | 38830     | I32 / 10 / RO     | VA                                            | -          | -                   | -                                    | Tylko P3.                                            |
|   | ... (R/S/T Apparent)                 | 38832+    | I32 / 10 / RO     | VA                                            | -          | -                   | -                                    | Tylko P3.                                            |
|   | Meter1/CT1 Combined Power Factor     | 38838     | I32 / 1000 / RO   | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | ... (R/S/T Power Factor)             | 38840+    | I32 / 1000 / RO   | -                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Meter1/CT1 Frequency                 | 38846     | I32 / 100 / RO    | Hz (2 regs)                                   | 31015     | int16 / 0.01 / RO   | Hz Phase R                           | Różne typy/gain.                                     |
|   | Meter2/CT2 Connection State          | 38901     | U16 / N/A / RO    | 0=Disconnect, 1=Connect                       | -          | -                   | -                                    | Tylko P3.                                            |
|   | ... (Meter2 fazy analogicznie)       | 38902+    | I32 / 10-1000 / RO| V/A/W/var/VA/PF/Hz                            | -          | -                   | -                                    | Tylko P3 (drugi CT).                                 |

### 6. Runtime – PV, Grid, Inverter, Load, EPS (wybrane z PDF + runtime)

| Nr | Sygnał name                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres / Opis                  | H3 Address | H3 Typ / Scale / RW | H3 Jednostka / Opis                  | Uwagi / Różnice                                      |
|----|--------------------------------------|------------|--------------------|-----------------------------------------------|------------|---------------------|--------------------------------------|------------------------------------------------------|
|   | Rated Power (Pn)                     | 39053     | I32 / 1000 / RO   | kW                                            | -          | -                   | -                                    | Tylko P3.                                            |
|   | Max Active Power (Pmax)              | 39055     | I32 / 1000 / RO   | kW                                            | -          | -                   | -                                    | Tylko P3.                                            |
|   | Status 1                             | 39063     | U16 / N/A / RO    | Bitfield                                      | 31041     | uint16 / 1 / RO     | Inverter State                       | Różne.                                               |
|   | Status 3                             | 39065     | U32 / N/A / RO    | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|   | Alarm 1                              | 39067     | U16 / N/A / RO    | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|   | Alarm 2                              | 39068     | U16 / N/A / RO    | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|   | Alarm 3                              | 39069     | U16 / N/A / RO    | Bitfield                                      | -          | -                   | -                                    | Tylko P3.                                            |
|   | PV1 Voltage                          | 39070     | I16 / 10 / RO     | V                                             | 31000     | int16 / 0.1 / RO    | V                                    | Różne gain.                                          |
|   | PV1 Current                          | 39071     | I16 / 100 / RO    | A                                             | 31001     | int16 / 0.1 / RO    | A                                    | Różne gain.                                          |
|   | ... (PV2–PV24 analogicznie)          | 39072+    | I16 / 10-100 / RO | V/A                                           | -          | -                   | -                                    | P3 do 24, H3 2-3.                                    |
|   | Total PV Input Power                 | 39118     | I32 / 1000 / RO   | kW                                            | -          | -                   | -                                    | Tylko P3.                                            |
|   | Grid R Phase Voltage                 | 39123     | I16 / 10 / RO     | V                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Grid S Phase Voltage                 | 39124     | I16 / 10 / RO     | V                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Grid T Phase Voltage                 | 39125     | I16 / 10 / RO     | V                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Inverter Active Power                | 39134     | I32 / 1000 / RO   | kW                                            | -          | -                   | -                                    | Tylko P3.                                            |
|   | Cumulative Power Generation          | 39149     | U32 / 100 / RO    | kWh                                           | 32001     | int16 / 0.1 / RO    | kWh total                            | Różne typy.                                          |
|   | Load Combined Power                  | 39225     | I32 / 1 / RO      | W                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | EPS Combined Power                   | 39216     | I32 / 1 / RO      | W                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Combined Power               | 39237     | I32 / 1 / RO      | W                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Total PV Energy                      | 39601     | U32 / 100 / RO    | kWh                                           | 32001     | int16 / 0.1 / RO    | kWh total                            | Różne zakresy.                                       |
|   | Daily PV Energy                      | 39603     | U32 / 100 / RO    | kWh                                           | 32002     | int16 / 0.1 / RO    | kWh daily                            | Podobnie.                                            |
|   | Battery Charge Energy Total          | 39605     | U32 / 100 / RO    | kWh                                           | 32004     | int16 / 0.1 / RO    | kWh charge                           | Różne typy.                                          |
|   | Battery Discharge Energy Total       | 39609     | U32 / 100 / RO    | kWh                                           | 32007     | int16 / 0.1 / RO    | kWh discharge                        | Podobnie.                                            |
|   | Load Energy Total                    | 39629     | U32 / 100 / RO    | kWh                                           | 32022     | int16 / 0.1 / RO    | kWh load                             | Różne typy.                                          |

### 7. Ustawienia RW (pełna lista z PDF + H3 charge periods)

| Nr | Sygnał name                          | P3 Address | P3 Typ / Gain / RW | P3 Jednostka / Zakres / Opis                  | H3 Address | H3 Typ / Scale / RW | H3 Jednostka / Opis                  | Uwagi / Różnice                                      |
|----|--------------------------------------|------------|--------------------|-----------------------------------------------|------------|---------------------|--------------------------------------|------------------------------------------------------|
|   | Factory Reset                        | 45002     | U16 / 1 / WO      | 1=Active                                      | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Power Active                 | 45003     | U16 / N/A / WO    | 0=Invalid, 1=Active                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Power Shut-down              | 45005     | U16 / N/A / WO    | 0=Invalid, 1=Active                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Power ON/OFF                 | 45006     | U16 / N/A / RO    | 0=OFF, 1=ON                                   | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Connect Enable               | 45007     | U16 / N/A / RW    | 0=Disable, 1=Enable                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | Remote Control                       | 46001     | Bitfield16 / N/A / RW | Bit0=Enable, Bit1=Direction, Bits3-2=Target | -          | -                   | -                                    | Tylko P3 (advanced).                                 |
|   | Import Power Limit                   | 46501     | I32 / 1 / RW      | W                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Threshold SOC                        | 46503     | U16 / 1 / RW      | %                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Export Peak Limit                    | 46504     | I32 / 1 / RW      | W                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | ChrInLowImport                       | 46506     | U16 / 1 / RW      | N/A                                           | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Max Charge Current           | 46607     | I16 / 10 / RW     | A                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Battery Max Discharge Current        | 46608     | I16 / 10 / RW     | A                                             | -          | -                   | -                                    | Tylko P3.                                            |
|   | Min SoC                              | 46609     | U16 / 1 / RW      | % [10-100]                                    | 41000     | uint16 / 1 / RW     | % [10-100]                           | Różne adresy.                                        |
|   | Max SoC                              | 46610     | U16 / 1 / RW      | % [10-100]                                    | -          | -                   | -                                    | Tylko P3.                                            |
|   | Min SoC OnGrid                       | 46611     | U16 / 1 / RW      | % [10-100]                                    | 41001     | uint16 / 1 / RW     | % [10-100]                           | Podobne.                                             |
|   | Export Power Limit                   | 46616     | I32 / 1 / RW      | W [0-Pmax]                                    | -          | -                   | -                                    | Tylko P3.                                            |
|   | Time Mode Flag                       | 48000     | U16 / 1 / RW      | 0=Disable, 1=Enable                           | -          | -                   | -                                    | Tylko P3 (time periods).                             |
|   | Grid Standard Code                   | 49079     | U16 / N/A / RW    | See PDF 4.2 (0-97 codes)                      | -          | -                   | -                                    | Tylko P3.                                            |
|   | Grid Point Power Limit               | 49136     | I32 / 1 / RW      | W [0-Pmax]                                    | -          | -                   | -                                    | Tylko P3.                                            |
|   | MPPT Switch                          | 49210     | U16 / N/A / RW    | 0=Disable, 1=Enable                           | -          | -                   | -                                    | Tylko H3.                                            |

## Podsumowanie i rekomendacje

- P3 ma **dużo więcej szczegółów** (multi-BMS/Meter, cell voltages, faults bitfields, remote control, 24 PV/MPPT, time groups).
- H3 ma prostsze runtime (31000+) i charge periods (41000+), ale brak wielu zaawansowanych funkcji P3.
- **Następne kroki**:
  - Użyj raw Modbus HA dla P3 (slave 247, holding, scale wg gain).
  - Fork repo nathanmarlor/foxess_modbus i dodaj mapę P3.
  - Dodaj skrypty Python do testów (mbpoll / pymodbus).
  - Zgłaszaj PR z nowymi rejestrami/testami.

