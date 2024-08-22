from uart_manager import UARTManager  # Importa la clase UARTManager
from PySide6 import QtCore
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import QTimer, Qt
import os
import sys


response_commands = [
    "CRYOCOOLER POWER MEASURED",
    "HOT HEAT SINK TEMPERATURE",
    "CRYOCOOLER COLD-TIP TEMPERATURE",
    "PRESSURE",
    "CHILLER COMPRESSOR SPEED",
    "CHILLER TEMPERATURE",
    "DEFROSTER CURRENT",
    "DEFROSTER TEMPERATURE",
    "MAX31865 TEMPERATURE",
    "NTC1 TEMPERATURE",
    "NTC2 TEMPERATURE",
    "FDC1004 CAPACITANCE",
#"INA213\t\t%s\t\t%s\r\n""TLE9201SG\t\t%s\t%s\r\n""ADS1118\t\t%s\t\t%s\r\n""DEFROSTER\t\t%s\t\t%s\r\n\r\n"
#"CRYOCOOLER\t\t%s\t\t%s\r\n""REFRIGERATION\t\t%s\t\t%s\r\n""ADS1118\t\t%s\t\t%s\r\n""CRYOPRESSURE\t\t%s\t\t%s\r\n\r\n"
#"LVL_SENSOR\t\t%s\t\t%s\r\n""PT100\t\t%s\t\t%s\r\n""NTC1\t\t%s\t\t%s\r\n""NTC2\t\t%s\t\t%s\r\n\r\n"
]


commands = [
    "SET DEFROSTER TARGET TEMP",
    "SET DEFROSTER NORMAL TEMP",
    "SET DEFROSTER MIN TEMP",
    "SET DEFROSTER MIN CURRENT",
    "SET DEFROSTER MAX TEMP",
    "SET DEFROSTER MAX CURRENT",
    "SET DEFROSTER STOP TIME SSR",
    "SET DEFROSTER STOP TIME FAN",
    "GET DEFROSTER STATE",
    "GET DEFROSTER INFO",
    "SET CRYOPRESSURE START",
    "SET CRYOPRESSURE STOP",
    "SET CRYOPRESSURE SHUTDOWN TEMP",
    "SET CRYOPRESSURE DANGER TEMP",
    "SET CHILLER SPEED",
    "SET CRYOCOOLER OPERATING PARAMETER 10",
    "SET CRYOCOOLER OPERATING PARAMETER 3",
    "SET CRYOCOOLER OPERATING PARAMETER 5",
    "SET CRYOCOOLER OPERATING PARAMETER 1",
    "GET DAQ RTD RES",
    "GET DAQ NTC1 RES",
    "GET DAQ NTC2 RES",
    "GET DAQ NITROGEN LVL",
    "GET DAQ STATE",
    ###########################################
    "GET DAQ MAX31865 TEMP",
    "GET DAQ NTC1 TEMP",
    "GET DAQ NTC2 TEMP",
    "GET DAQ FDC1004 CAP",
    "GET DEFROSTER TEMP",
    "GET DEFROSTER CURRENT",
    "GET PRESSURE",
    #"GET PS TEMP",
    "GET CRYOCOOLER COLD TIP TEMP",
    "GET CRYOCOOLER HOT HEAT SINK TEMP",
    "GET CRYOCOOLER POWER OUTPUT",
    "GET CHILLER SPEED",
    "GET CHILLER TEMPERATURE",
    ############################################
    "GET CRYOCOOLER POWER INPUT",
    "GET CHILLER CURRENT",
    "GET CHILLER TROUBLECODE",
    "GET CHILLER DATA",
    "GET CRYOPRESSURE INFO",
    "GET DAQ INFO",
]



base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
ui_path = os.path.join(base_path, 'clone-dashboard.ui')
ui, _ = loadUiType(ui_path)

#ui, _ = loadUiType("./clone-dashboard.ui")


# run pyside6-rcc <your_resource.qrc> -o your_resource.py



class DashWindow(QMainWindow, ui):
    def __init__(self):
        super(DashWindow, self).__init__()
        # Remove default title bar
        flags = Qt.WindowFlags(Qt.FramelessWindowHint)  # | Qt.WindowStaysOnTopHint -> put windows on top
        self.setMaximumSize(1600, 720)
        self.setWindowFlags(flags)
        self.setupUi(self)
        self.showNormal()
        self.offset = None

        self.i=20
        self.temp_value = self.lineEdit.text()
        #UART INITIALIZATION
        self.uart = UARTManager()
        self.uart_buffer = ""

        self.lineEdit_2.returnPressed.connect(self.handle_text_change)
        self.lineEdit.returnPressed.connect(self.handle_text_change)
        self.write_cryocoolerParameter.returnPressed.connect(self.handle_text_change)

        # Inicializar el temporizador
        #self.timer = QTimer(self)
        #self.timer.timeout.connect(self.data_request)
        #self.timer.start(1000) 

        self.receive_timer = QTimer(self)
        self.receive_timer.timeout.connect(self.read_uart_data)
        self.receive_timer.start(1)

        self.pushButton_4.clicked.connect(self.close_win)
        self.pushButton_6.clicked.connect(self.minimize_win)
        self.pushButton_5.clicked.connect(self.mini_maximize)
        

    def handle_text_change(self):
        #self.timer.stop() 
        self.receive_timer.stop()
        sender = self.sender()  # Identifica cuál QLineEdit fue modificado
        if sender == self.lineEdit:
            self.command_to_send = commands[15]  # Selecciona comando 1
            self.temp_value = self.lineEdit.text()
            self.lineEdit.clear()
        elif sender == self.lineEdit_2:
            self.command_to_send = commands[14]  # Selecciona comando 2
            self.temp_value = self.lineEdit_2.text()
            self.lineEdit_2.clear()
        elif sender == self.write_cryocoolerParameter:
             match self.comboBox.currentText():
                case "SOFT STOP MODE":
                    self.command_to_send = commands[16]
                    print(f'soft stop mode{self.write_cryocoolerParameter.text()}')
                case "PID MODE":
                    self.command_to_send = commands[17]
                    print(f'pid mode{self.write_cryocoolerParameter.text()}')
                case "TSTAT MODE":
                 self.command_to_send = commands[18]
                 print(f'tstat mode{self.write_cryocoolerParameter.text()}')
                case _:
                    print(f'Comando no manejado: in case (handle_text_change function)')
        self.temp_value = self.write_cryocoolerParameter.text()
        self.write_cryocoolerParameter.clear()

        self.send_uart_command()

    def get_text(self):
        entered_text =self.lineEdit.text()
        self.uart_data =entered_text

    def send_uart_command(self):

        if hasattr(self, 'command_to_send'):
            entered_value = self.temp_value # Obtén el valor ingresado en el LineEdit
            command = f"{self.command_to_send} {entered_value}"  # Agrega un espacio y el valor al comando
            response = self.uart.send_command(command)
            if response is not None:
                print(f'Comando enviado: {command}')
                #self.update_label(response)
            else:
                print('Error al enviar el comando')
        #else:
           # self.show_error("No se ha seleccionado ningún comando")
        #self.timer.start(1000)
        self.receive_timer.start(1)

    def strncmp(self,str1, str2, n):
        if str1[:n] == str2[:n]:
            return 1
        else:
            #print("false")
            return 0

    def data_request(self):
        #print("Enviando solicitud de datos...")
        self.uart.send_command(commands[self.i])
        self.i = self.i+1
        if self.i == 32:
            self.i=21
        print(f'Requesting command... ->{commands[self.i]}')
        #self.uart.send_command(commands[21])
        #self.uart.send_command(commands[18])
        #print(commands[22])

    def read_uart_data(self):
        # Leer datos disponibles desde UART
        data = self.uart.read_data()
        if data:
           # print(f'Datos recibidos: {data}')
            cleaned_data = data.replace('\0', '')
            # Añadir los datos limpios al buffer
            self.uart_buffer = cleaned_data
            # Procesar el buffer
            self.process_received_data(self.uart_buffer)

    def process_received_data(self, data):
        data = data.strip()
        print("Proccessing data...")
         # Quitar espacios en blanco alrededor
        for command in response_commands:
            command = command.strip()      
            if self.strncmp(data, command, len(command)):
                # Dividir el comando y el valor
                parts = data[len(command):].strip()  # Parte después del comando
                if parts:
                    value = parts  # El valor asociado
                    self.update_ui_based_on_command(command, value)
                else:
                    print('Here1')
                break
            ##else:
              ##  print(f'Comando no reconocido: {data}')

    def update_ui_based_on_command(self, command, value):
        print(command)
        print(value)
        match command:
            case "MAX31865 TEMPERATURE":
                self.read_tankTemperature.setText(str(value))
            case "NTC1 TEMPERATURE":
                self.read_ambientTemperature.setText(str(value))
            case "NTC2 TEMPERATURE":
                self.read_ardiInternalTemperature.setText(str(value))
            case "HOT HEAT SINK TEMPERATURE":
                self.read_HHSTemperature.setText(str(value))
            case "FDC1004 CAPACITANCE":
                self.read_nitrogenLevel.setText(str(value))
            case "DEFROSTER TEMPERATURE":
                self.read_defrosterTemperature.setText(str(value))
            case "DEFROSTER CURRENT":
                self.read_defrosterCurrent.setText(str(value))
            case "CRYOCOOLER COLD-TIP TEMPERATURE":
                self.read_coldTipTemperature.setText(str(value))
            case "CHILLER TEMPERATURE":
                self.read_coolantLiquidTemperature.setText(str(value))
            case "PRESSURE":
                self.read_pressure.setText(str(value))
            case "CHILLER COMPRESSOR SPEED":
                self.read_chillerSpeed.setText(str(value))
            case "CRYOCOOLER POWER MEASURED":
                self.read_powerValue.setText(str(value))
            case _:
                print(f'Comando no manejado: {response_commands}')

    def get_selected_option(self):
        # Método para obtener la opción seleccionada
        return 0  # Cambia esto según la lógica de selección
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def close_win(self):
        self.close()

    def mini_maximize(self):
        if self.isMaximized():
            self.pushButton_5.setIcon(QIcon("./resources/icons/maximize.svg"))
            self.showNormal()
        else:
            self.pushButton_5.setIcon(QIcon("./resources/icons/minimize.svg"))
            self.showMaximized()

    def minimize_win(self):
        self.showMinimized()

    ### *****UART METHODS***** ###

    def get_selected_option(self):
        # Este método debería devolver el índice del comando seleccionado
        # Para propósitos demostrativos, usamos un valor fijo
        # Reemplaza este método con la lógica adecuada para obtener el índice
        return 0  # Cambia esto según la lógica de selección

    def closeEvent(self, event):
        self.uart.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication()
    window = DashWindow()
    window.show()

    sys.exit(app.exec())
