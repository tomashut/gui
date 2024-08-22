# uart_manager.py

import serial

class UARTManager:
    def __init__(self, port='COM5', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
    
    def send_command(self, command):
        try:
            self.ser.write(command.encode('ascii'))
            # Espera una respuesta si es necesario
            response = self.ser.readline().decode('ascii').strip()
            return response
        except serial.SerialException as e:
            print(f"Error en el puerto serial: {e}")
            return None

    def read_data(self):
        try:
            if self.ser.in_waiting > 0:
                data = self.ser.readline().decode('ascii').strip()
                return data
            return None
        except serial.SerialException as e:
            print(f"Error en el puerto serial: {e}")
            return None

    def close(self):
        self.ser.close()
