# Importamos las librerías necesarias
from machine import Pin, SPI  # Para controlar los pines GPIO y la comunicación SPI en un microcontrolador
from nrf24l01 import NRF24L01  # Para manejar el módulo de radiofrecuencia NRF24L01
import network  # Para gestionar la conexión WiFi
import struct  # Para convertir datos en bytes antes de transmitirlos
import time  # Para manejar pausas y retardos

# === Configuración de los pines y SPI para el NRF24L01 ===
csn = Pin(5, mode=Pin.OUT, value=1)   # Pin de selección de chip (CSN), inicializado en HIGH (inactivo)
ce = Pin(6, mode=Pin.OUT, value=0)    # Pin de habilitación del módulo (CE), inicializado en LOW (desactivado)

# Configuración del bus SPI en los pines especificados
spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))  
# SPI(0) -> Bus SPI 0
# sck=Pin(2) -> Pin del reloj SPI
# mosi=Pin(3) -> Pin de salida de datos (Master Out Slave In)
# miso=Pin(4) -> Pin de entrada de datos (Master In Slave Out)

# === Configuración de la conexión WiFi ===
wifi = network.WLAN(network.STA_IF)  # Se configura la interfaz WiFi en modo estación (STA)
wifi.active(True)  # Activamos la interfaz WiFi

# Credenciales de la red WiFi
SSID = "iPhone de Daniel"  
PASSWORD = "quimica123"

# Intentamos conectar el microcontrolador a la red WiFi
wifi.connect(SSID, PASSWORD)

# Esperamos hasta 10 segundos a que se establezca la conexión WiFi
for _ in range(20):  # 20 iteraciones de 0.5s cada una = 10 segundos máximo
    if wifi.isconnected():  # Si la conexión es exitosa, salimos del bucle
        break
    time.sleep(0.5)  # Espera de medio segundo antes de volver a verificar

# Verificamos si logramos conectarnos o no
if wifi.isconnected():
    print("Conectado a WiFi:", wifi.ifconfig()[0])  # Mostramos la dirección IP asignada
else:
    print("No se pudo conectar a WiFi")  # Mensaje de error si la conexión falla

# === Configuración del NRF24L01 ===
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")  
# Se configuran las direcciones de comunicación de los módulos NRF24L01 (en formato binario)

# Inicializamos el módulo NRF24L01
nrf = NRF24L01(spi, cs=csn, ce=ce, channel=122, payload_size=1)  
# channel=122 -> Canal de transmisión (2.522 GHz)
# payload_size=1 -> Se define el tamaño del mensaje en 1 byte

# Configuramos la velocidad de transmisión y la potencia del NRF24L01
nrf.reg_write(0x06, 0b00100110)  
# Registro 0x06:
# - 250kbps de velocidad de datos
# - Potencia de salida en 0dBm

# Configuramos los pipes de transmisión y recepción
nrf.open_tx_pipe(pipes[0])  # Establecemos la dirección del pipe para transmisión
nrf.open_rx_pipe(1, pipes[1])  # Establecemos la dirección del pipe para recepción en la posición 1

# === Bucle principal de transmisión del RSSI ===
while True:
    if wifi.isconnected():  # Verificamos si seguimos conectados a la red WiFi
        rssi = wifi.status('rssi')  # Obtenemos la intensidad de la señal WiFi en dBm

        if rssi is not None:  # Verificamos que el RSSI sea válido
            try:
                nrf.stop_listening()  # Detenemos la escucha para poder transmitir datos
                print("Enviando RSSI:", rssi, "dBm")  # Mostramos el RSSI en la consola
                nrf.send(struct.pack("b", rssi))  # Convertimos el RSSI en un byte con signo y lo enviamos
            except OSError:  # Capturamos errores en la transmisión
                print("Error en la transmisión")  # Mensaje de error si no se puede enviar el dato

    else:  # Si la conexión WiFi se pierde
        print("WiFi desconectado, intentando reconectar...")  
        wifi.connect(SSID, PASSWORD)  # Intentamos reconectar a la red WiFi

    time.sleep(1)  # Esperamos 1 segundo antes de enviar el siguiente valor RSSI
