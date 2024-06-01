import serial
from struct import pack, unpack
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import itertools
import numpy as np
from pynput import keyboard

# Se configura el puerto y el BAUD_Rate
PORT = 'COM3'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32
WINDOW = 128

KEYBOARD_INPUT = ""
SUSPENDED = False
keys = dict([('p1', 'Suspend Power Mode'),
             ('p2', 'Lower Power Mode'), 
             ('p3', 'Normal Power Mode'), 
             ('p4', 'Performance Power Mode'), 
             ('s1', 'Cambio a rango +/-2g'), 
             ('s2', 'Cambio a rango +/-4g'), 
             ('s3', 'Cambio a rango +/-8g'), 
             ('s4', 'Cambio a rango +/-16g'), 
             ('a1', 'Cambio frecuencia de muestreo 200hz'),
             ('a2', 'Cambio frecuencia de muestreo 400hz'),
             ('a3', 'Cambio frecuencia de muestreo 800hz'),
             ('a4', 'Cambio frecuencia de muestreo 1600hz')])
def on_press(key):
    global KEYBOARD_INPUT
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other key
    if k in ['1', '2', '3', '4', 'a', 's', 'p']:  # keys of interest
        KEYBOARD_INPUT += k
        if (len(KEYBOARD_INPUT) == 2):
            if (keys.get(KEYBOARD_INPUT)):
                keys.get(KEYBOARD_INPUT)
                print('Input recived:', keys.get(KEYBOARD_INPUT))
            else:
                KEYBOARD_INPUT = ""
                print('Invalid Input')
                printModoDeUso()

def printModoDeUso():
    print("===========[Modo de uso]===========")
    for x, y in keys.items():
        print(x, ':', y)
    print("===================================")

printModoDeUso()

listener = keyboard.Listener(on_press=on_press)
listener.start()  # start to listen on a separate thread
# listener.join()  # remove if main thread is polling self.keys

# Se abre la conexion serial
ser = serial.Serial(PORT, BAUD_RATE, timeout = 1)
# Funciones
def send_message(message):
    """ Funcion para enviar un mensaje a la ESP32 """
    ser.write(message)

def receive_response():
    """ Funcion para recibir un mensaje de la ESP32 """
    response = ser.readline()
    return response

def receive_data():
    """ Funcion que recibe tres floats (fff) de la ESP32 
    y los imprime en consola """
    data = receive_response()
    print(f"Data = {data}")
    data = unpack("fff", data)
    print(f'Received: {data}')
    return data

def send_end_message():
    """ Funcion para enviar un mensaje de finalizacion a la ESP32 """
    end_message = pack('4s', 'END\0'.encode())
    ser.write(end_message)

# Se inicializa el gráfico
fig, axs = plt.subplots(2, 2)
xlist, accx, accy, accz = [], [], [], []
RMSx, RMSy, RMSz = [], [], []
FFTx, FFTy, FFTz = [], [], []
xlistpeaks, Peaksx, Peaksy, Peaksz = [], [], [], []
xlistfft = []

ln, = axs[0, 0].plot([], [], 'ro')
ln2, = axs[0, 1].plot([], [], 'ro')
ln3, = axs[1, 0].plot([], [], 'ro')
ln4, = axs[1, 1].plot([], [], 'ro')

index = 0

def i_gen():
    for cnt in itertools.count():
        yield cnt

def init():
    axs[0, 0].set_title('Aceleración')
    axs[0, 0].set_ylim(-4, 4)
    axs[0, 1].set_title('RMS')
    #axs[0, 1].set_ylim(-10, 10)
    axs[1, 0].set_title('FFT')
    axs[1, 1].set_title('Peaks')
    axs[1, 1].set_ylim(-30, 30)

def update(i, xlist, accx, accy, accz, RMSx, RMSy, RMSz, FFTx, FFTy, FFTz, xlistpeaks, Peaksx, Peaksy, Peaksz, xlistfft):
    global index
    global KEYBOARD_INPUT
    global SUSPENDED
    # Read the sensor data
    if ser.in_waiting > 0:
        try:
            response = ser.readline()
            if (len(KEYBOARD_INPUT) == 2):
                send_message(f"{KEYBOARD_INPUT}\0".encode())
                KEYBOARD_INPUT = ""

            if response.decode().strip("\r\n") == "ERROR":
                if SUSPENDED == False:
                    print("Seleccione otro modo para salir de la suspención")
                SUSPENDED = True
                return
            SUSPENDED = False
            #print("DATOS")
            #print(response)
    
            dataRows = response.decode().strip("; \r\n").split("; ")

            accDatax, accDatay, accDataz = dataRows[:3]
            new_accx = [float(x) for x in accDatax.split(", ")]
            new_accy = [float(y) for y in accDatay.split(", ")]
            new_accz = [float(z) for z in accDataz.split(", ")]

            RMSDatax, RMSDatay, RMSDataz = dataRows[3:6]
            newRMSx = [float(x) for x in RMSDatax.split(", ")]
            newRMSy = [float(y) for y in RMSDatay.split(", ")]
            newRMSz = [float(z) for z in RMSDataz.split(", ")]
            
            FFTDatax, FFTDatay, FFTDataz = dataRows[6:9]

            newFFTx = [2*np.abs(complex(x.strip()))/WINDOW for x in FFTDatax.split(", ")]
            newFFTy = [2*np.abs(complex(y.strip()))/WINDOW for y in FFTDatay.split(", ")]
            newFFTz = [2*np.abs(complex(z.strip()))/WINDOW for z in FFTDataz.split(", ")]

            PeaksDatax, PeaksDatay, PeaksDataz = dataRows[9:12]
            newPeaksx = [float(x) for x in PeaksDatax.split(", ")]
            newPeaksy = [float(y) for y in PeaksDatay.split(", ")]
            newPeaksz = [float(z) for z in PeaksDataz.split(", ")]

            # Add the data to the lists
            xlist += list(range(index*WINDOW, ((index+1)*WINDOW)))
            accx += new_accx
            accy += new_accy
            accz += new_accz

            RMSx += newRMSx
            RMSy += newRMSy
            RMSz += newRMSz

            xlistfft = list(range(0, int(WINDOW/2)))
            FFTx = newFFTx[0:int(WINDOW/2)]
            FFTy = newFFTy[0:int(WINDOW/2)]
            FFTz = newFFTz[0:int(WINDOW/2)]

            xlistpeaks += list(range(index*5, (index+1)*5))
            Peaksx += newPeaksx
            Peaksy += newPeaksy
            Peaksz += newPeaksz
            
            # Limit lists to 1000 items
            xlist = xlist[-1000:]
            accx = accx[-1000:]
            accy = accy[-1000:]
            accz = accz[-1000:]
            
            RMSx = RMSx[-1000:]
            RMSy = RMSy[-1000:]
            RMSz = RMSz[-1000:]

            xlistpeaks = xlistpeaks[-50:]
            Peaksx = Peaksx[-50:]
            Peaksy = Peaksy[-50:]
            Peaksz = Peaksz[-50:]
            # Draw data
            axs[0, 0].clear()
            axs[0, 0].set_title('Aceleración')
            axs[0, 0].set_ylim(-4, 4)
            axs[0, 0].plot(xlist, accx, color="blue", label = "Eje x")
            axs[0, 0].plot(xlist, accy, color="red", label = "Eje y")
            axs[0, 0].plot(xlist, accz, color="green", label = "Eje z")
            axs[0, 0].legend()

            axs[0, 1].clear()
            axs[0, 1].set_title('RMS')
            #axs[0, 1].set_ylim(60000, 70000)
            axs[0, 1].plot(xlist, RMSx, color="blue", label = "Eje x")
            axs[0, 1].plot(xlist, RMSy, color="red", label = "Eje y")
            axs[0, 1].plot(xlist, RMSz, color="green", label = "Eje z")
            axs[0, 1].legend()

            axs[1, 0].clear()
            axs[1, 0].set_title('FFT')
            #axs[1, 0].set_ylim(-10, 10)
            axs[1, 0].plot(xlistfft, FFTx, color="blue", label = "Eje x")
            axs[1, 0].plot(xlistfft, FFTy, color="red", label = "Eje y")
            axs[1, 0].plot(xlistfft, FFTz, color="green", label = "Eje z")
            axs[1, 0].legend()

            axs[1, 1].clear()
            axs[1, 1].set_title('Peaks')
            axs[1, 1].set_ylim(-30, 30)
            axs[1, 1].plot(xlistpeaks, Peaksx, color="blue", label = "Eje x")
            axs[1, 1].plot(xlistpeaks, Peaksy, color="red", label = "Eje y")
            axs[1, 1].plot(xlistpeaks, Peaksz, color="green", label = "Eje z")
            axs[1, 1].legend()

            index += 1

        except KeyboardInterrupt:
            print('Finalizando comunicacion')
            
        """ except:
            print('Error en leer mensaje') """


# # Se lee data por la conexion serial
# counter = 0
# while True:
#     if ser.in_waiting > 0:
#         response = ser.readline()
#         parsed = str(response.decode()).replace("\r", "").replace("\n", "")
#         if parsed == "BEGIN":
#             send_message("OK\0".encode())
#             print("Conexión establecida")
#             break
#         else:
#             print("PARSED",parsed)


# while True:
#     if ser.in_waiting > 0:
#         try:
#             response = ser.readline()
#             print("DATOS")
#             print(response)
#         except KeyboardInterrupt:
#             print('Finalizando comunicacion')
#             break
#         except:
#             print('Error en leer mensaje')
#             continue

# anim = FuncAnimation(fig, update, i_gen, init_func=init, save_count=200, fargs=(xlist, accx, accy, accz, RMSx, RMSy, RMSz, FFTx, FFTy, FFTz, xlistpeaks, Peaksx, Peaksy, Peaksz, xlistfft))
# plt.show()


import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog


class ConfigDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('Graph.ui', self)  # Load the .ui file

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ConfigDialog()
    dialog.show()
    sys.exit(app.exec_())
