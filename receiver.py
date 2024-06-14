import serial
from struct import pack, unpack
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import itertools
import numpy as np

# Se configura el puerto y el BAUD_Rate
PORT = 'COM3'  # Esto depende del sistema operativo
BAUD_RATE = 115200  # Debe coincidir con la configuracion de la ESP32
WINDOW = 128

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

index = 0

def i_gen():
    for cnt in itertools.count():
        yield cnt

def init_connection(sensibility, odr, power_mode):
    step = 0
    while True:
        if ser.in_waiting > 0:
            response = ser.readline()
            parsed = str(response.decode()).replace("\r", "").replace("\n", "")
            if parsed == "BEGIN":
                send_message("OK\0".encode())
                if step == 0:
                    print("Conectando...")
                step = 1
            elif step == 1 and parsed == "OK":
                print("Conexión establecida")
                break
            else:
                print("PARSED",parsed)

    send_message(f"{sensibility}{odr}{power_mode}\0".encode())




def init_receiver():
    if ser.in_waiting > 0:
        try:
            response = ser.readline()
            if response.decode().strip("\r\n") == "ERROR":
                pass
            if response.decode().strip("\r\n") == "BEGIN":
                pass

            # print("DATOS")
            # print(response)

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

            return new_accx, new_accy, new_accz, newRMSx, newRMSy, newRMSz, newFFTx, newFFTy, newFFTz, newPeaksx, newPeaksy, newPeaksz


        except KeyboardInterrupt:
            print('Finalizando comunicacion')
            
        """ except:
            print('Error en leer mensaje') """