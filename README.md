# Proyecto de Microcontroladores con ESP32, Sensor Inercial BOSCH BMI270 y Sensor Ambiental BOSCH BME688.

## Descripción

Este proyecto consiste en la integración de un microcontrolador ESP32 con un sensor inercial BOSCH BMI270 y uno ambiental BOSCH BME688. Se establece una comunicación serial I2C entre el ESP32 y los sensores para controlar su configuración y obtener mediciones. Estas mediciones se transmiten a un computador a través de una conexión serial UART, donde serán mostradas en una interfaz gráfica de usuario (GUI) desarrollada con QT5.

## Características del Sensor Inercial (IMU) BMI270

El sensor BMI270 tiene diferentes modos de poder, configuraciones y mediciones:

- **Modos de poder:**
  - Modo de bajo rendimiento
  - Modo de medio rendimiento
  - Modo de alto rendimiento
  - Modo de suspensión
- **Configuraciones adicionales:**
  - Sensibilidad del giroscopio y acelerómetro: +/-2g, +/-4g, +/-8g, +/-16g
  - Frecuencia de muestreo (ODR): 200Hz, 400Hz, 800Hz, 1600Hz
- **Mediciones:**
  - Aceleración (x, y, z)
  - Velocidad angular (x, y, z)
  - Transformada de Fourier (FFT) (x, y, z)
  - RMS (Root Mean Square) (x, y, z)
  - Últimos 5 picos (x, y, z)

## Características del Sensor Ambiental BME688

El sensor BME688 tiene diferentes modos de uso, configuraciones y mediciones:

- **Modos de uso:**
  - Modo Forzado
  - Modo Paralelo
  - Modo de Suspensión (Sleep)
- **Mediciones:**
  - Temperatura
  - Humedad
  - Presión
  - CO (Calidad del aire)

## Interfaz Gráfica de Usuario (GUI)

La GUI se ha desarrollado utilizando la librería QT5 y cumple las siguientes funcionalidades:

- Conectar la ESP32 con el sensor conectado (BMI270 o BME688).
- Detectar automáticamente cuál sensor está conectado o permitir seleccionar manualmente a través de una lista desplegable.
- Obtener y cambiar el modo de poder/funcionamiento del sensor conectado.
- Obtener y cambiar la sensibilidad y la frecuencia de muestreo del sensor BMI270.
- Recibir y visualizar en tiempo real todas las mediciones enviadas por los sensores, graficándolas en un plot dentro de la interfaz.

## Recursos

- [Datasheet del BMI270](https://www.bosch-sensortec.com/products/motion-sensors/imus/bmi270/)
- [Datasheet del BME688](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors/bme688/)
- [Documentación ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/)

## Video Demostración

Para una demostración visual del proyecto, ver el siguiente video: [Video Demostración](https://youtu.be/tTdplMQtxio)
