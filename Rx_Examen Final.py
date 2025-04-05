from machine import Pin, SPI, I2C
import struct
import time
from nrf24l01 import NRF24L01
from ssd1306 import SSD1306_I2C

# === Pines SPI para NRF24L01 ===
csn = Pin(5, mode=Pin.OUT, value=1)   # Chip Select (CSN)
ce = Pin(6, mode=Pin.OUT, value=0)    # Chip Enable (CE)
spi = SPI(0, sck=Pin(2), mosi=Pin(3), miso=Pin(4))  # Bus SPI

# === Pines I2C para OLED ===
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# === Configuración NRF24L01 ===
pipes = (b"\xe1\xf0\xf0\xf0\xf0", b"\xd2\xf0\xf0\xf0\xf0")
nrf = NRF24L01(spi, csn, ce, channel=122, payload_size=1)  # Canal cambiado a 122
nrf.open_tx_pipe(pipes[1])  # Configura el pipe de transmisión
nrf.open_rx_pipe(1, pipes[0])  # Configura el pipe de recepción
nrf.stop_listening()  # Poner en modo recepción

# === Loop de recepción y visualización en OLED ===
while True:
    if nrf.any():  # Si hay datos en el buffer
        buf = nrf.recv()  # Recibir datos
        rssi = struct.unpack("b", buf)[0]  # Convertir byte a entero con signo

        print("RSSI recibido:", rssi, "dBm")  # Mostrar en consola

        # Mostrar en pantalla OLED
        oled.fill(0)
        oled.text("RSSI recibido:", 10, 20)
        oled.text(f"{rssi} dBm", 40, 40)
        oled.show()
    
    time.sleep(1)  # Corregida la indentación
