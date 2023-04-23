import serial
decoder = {
   0 : ("BATTERY_CAPACITY", "%", 1.0),
   1 : ("BATTERY_VOLTAGE", "V", 0.1),
   2 : ("CHARING_CURRENT", "A", 0.01),
   3 : ("TEMPERATURE_CNTLR", "C", 1.0, "TEMPERATURE_BATT", "C", 1.0),
  35 : ("TEMPERATURE_PICO", "C", 1.0),
   4 : ("STREET_LIGHT_VOLTAGE", "V", 0.1),
   5 : ("STREET_LIGHT_CURRENT", "A", 0.01),
   6 : ("STREET_LIGHT_POWER", "W", 1.0),
   7 : ("SOLAR_PANEL_VOLTAGE", "V", 0.1),
   8 : ("SOLAR_PANEL_CURRENT", "A", 0.01),
   9 : ("CHARGING_POWER", "W", 1.0),
  #10 : ("LIGHT_ON_OFF_COMMAND", "-", 1.0),
  11 : ("BATTERY_MIN_VOLTAGE_OF_DAY", "V", 0.1),
  12 : ("BATTERY_MAX_VOLTAGE_OF_DAY", "V", 0.1),
  13 : ("MAX_CHARGING_CURRENT_OF_DAY", "A", 0.01),
  14 : ("MAX_DISCHARGING_CURRENT_OF_DAY", "A", 0.01),
  15 : ("MAX_CHARGING_POWER_OF_DAY", "W", 1.0),
  16 : ("MAX_DISCHARGING_POWER_OF_DAY", "W", 1.0),
  19 : ("CHARGING_AH_OF_DAY", "AH", 1.0),
  18 : ("DISCHARGING_AH_OF_DAY", "AH", 1.0),
  19 : ("POWER_GENERATION_OF_DAY", "WH", 0.1),
  20 : ("POWER_CONSUMPTION_OF_DAY", "WH", 0.1),
  21 : ("TOTAL_OPERATING_DAYS", "-", 1.0),
  22 : ("TOTAL_BATTERY_OVER_DISCHARGES", "-", 1.0),
  23 : ("TOTAL_BATTERY_FULL_CHARGES", "-", 1.0),
  24 : ("TOTAL_CHARGING", "AH", 1.0, True),
  26 : ("TOTAL_DISCHARGING", "AH", 1.0, True),
  28 : ("CUMULATIVE_POWER_GENERATION", "WH", 0.1, True),
  30 : ("CUMULATIVE_POWER_CONSUMPTION", "WH", 0.1, True),
  32 : ("STREET_LIGHT_STATUS_CHARGING_STATE", "-", 1.0, False, "Hex"),
  33 : ("CONTROLLER_FAULT_WARNING", "-", 1.0, True, "Hex")
}


ser = serial.Serial('COM5',baudrate=115200,timeout=15)  # open serial port

ser.write(b'AT+ADDRESS?\r\n')
line = ser.readline().decode('utf-8')   # read a '\n' terminated line
print(f'{line}')

loopNames = {
    1 : 'MODEL    ',
    2 : 'SERIAL_NO',
    0 : 'DATA     ',
    9 : 'ERROR    '
}
timeoutCount = 0
while True:
    line = ser.readline().decode("utf-8")
    if len(line) > 0:
        timeoutCount = 0
        atParts = line.split(',')
        if 0 < len(atParts):
            #print(atParts[2])
            loopParts = atParts[2].split(':')
            if 0 < len(loopParts):
                index = int(loopParts[0])
                if index is not None:
                    data = loopParts[1]
                    print(f'{loopNames[index]} : {data}')
                    if index == 0:
                        for key, value in decoder.items():
                            #print(f'{key} : {value[0]} {len(value)}')
                            k = 4*key
                            if len(value) == 3:
                                x = int(data[k:k+4],16)
                                x = x * value[2]
                                print(f'{key:2d} : {value[0]} = {x:.1f} {value[1]}')
                            elif len(value) == 4:
                                x = int(data[k:k+8],16)
                                x = x * value[2]
                                print(f'{key:2d} : {value[0]} = {x:.1f} {value[1]}')
                            elif len(value) == 5:
                                if value[3] == True:
                                    s = 8
                                else:
                                    s = 4
                                print(f'{key:2d} : {value[0]} = {data[k:k+s]} {value[1]}')
                            elif len(value) == 6:
                                x = int(data[k:k+2],16)
                                x = x * value[2]
                                print(f'{key:2d} : {value[0]} = {x:.1f} {value[1]}')
                                x = int(data[k+2:k+4],16)
                                x = x * value[5]
                                print(f'{key:2d} : {value[3]} = {x:.1f} {value[4]}')                        
                                
    else:
        timeoutCount = timeoutCount + 1
        print(f'Timeout {timeoutCount}')

ser.close()

