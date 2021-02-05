import serial.tools.list_ports

available_ports = serial.tools.list_ports.comports()

if len(available_ports) > 0:
  for port in available_ports:
    print(f"{port[0]}\t{port[1]}\t{port[2]}")
