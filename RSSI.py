import network
import time
import math
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# Configuración OLED
WIDTH = 128
HEIGHT = 32
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=100000)
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Configuración WiFi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
ssid = "iPhone de Daniel"
password = "quimica123"

# Configuración de los LEDs
led_avanzar = Pin(16, Pin.OUT)
led_midiendo = Pin(17, Pin.OUT)
led_wifi = Pin(19, Pin.OUT)

# Configuración del pulsador
button = Pin(18, Pin.IN, Pin.PULL_UP)

# Función para conectar a WiFi
def connect_wifi():
    print("Conectando a WiFi...")
    led_wifi.value(1)
    wifi.connect(ssid, password)
    timeout = 10  # Tiempo máximo de espera en segundos
    start_time = time.time()
    
    while not wifi.isconnected():
        if time.time() - start_time > timeout:
            print("No se pudo conectar a WiFi")
            display_disconnected()
            return False
        time.sleep(0.5)
        led_wifi.value(not led_wifi.value())
    
    print("Conexión establecida!")
    print("Dirección IP:", wifi.ifconfig()[0])
    led_wifi.value(0)
    return True

def display_disconnected():
    oled.fill(0)
    oled.text("Desconectado", 2, 6)
    oled.show()
    while not wifi.isconnected():
        led_wifi.value(not led_wifi.value())
        time.sleep(1)  # Parpadeo más rápido
    connect_wifi()

def measure_rssi(distance):
    rssi_values = []
    led_midiendo.value(1)
    filename = f"rssi_measurements_{distance}m.txt"
    
    with open(filename, "w") as file:
        file.write("Tiempo (s)\tRSSI (dBm)\n")  # Encabezado
        for i in range(200):
            if not wifi.isconnected():
                display_disconnected()
                return [], 0, 0
            elapsed_time = i * 0.1  # Asegura que los tiempos sean 0.0, 0.1, 0.2, etc.
            rssi = wifi.status('rssi')
            rssi_values.append(rssi)
            file.write(f"{elapsed_time:.1f}\t{rssi}\n")
            display_rssi(rssi, distance)
            time.sleep(0.1)
    
    led_midiendo.value(0)
    rssi_average = sum(rssi_values) / len(rssi_values)
    variance = sum((x - rssi_average) ** 2 for x in rssi_values) / len(rssi_values)
    stddev_rssi = math.sqrt(variance)
    
    print(f"Distancia: {distance}m, Promedio RSSI: {rssi_average:.2f} dBm, Desviación: {stddev_rssi:.2f} dBm")
    
    with open(filename, "a") as file:
        file.write(f"\nResumen:\nDistancia: {distance}m\nPromedio RSSI: {rssi_average:.2f} dBm\nDesviación Estándar: {stddev_rssi:.2f} dBm\n")
    
    with open("rssi_measurements.txt", "a") as summary_file:
        summary_file.write(f"Distancia: {distance}m, Promedio: {rssi_average:.2f} dBm, Desv: {stddev_rssi:.2f} dBm\n")
    
    return rssi_values, rssi_average, stddev_rssi

def display_rssi(rssi, distance):
    max_rssi = -15
    min_rssi = -100
    bar_width = int((rssi - min_rssi) / (max_rssi - min_rssi) * WIDTH)
    bar_width = max(0, min(WIDTH, bar_width))
    
    oled.fill(0)
    oled.text(f"Dist: {distance}m", 2, 6)
    oled.text(f"RSSI: {rssi} dBm", 2, 16)
    oled.rect(2, 26, 124, 6, 1)
    oled.fill_rect(2, 26, bar_width, 6, 1)
    oled.show()

def display_measurement_start():
    oled.fill(0)
    oled.text("Iniciando medición", 2, 6)
    oled.show()
    led_avanzar.value(0)
    led_midiendo.value(1)

def display_measurement_done():
    oled.fill(0)
    oled.text("Medición terminada", 2, 6)
    oled.show()
    led_avanzar.value(1)
    led_midiendo.value(0)

def leds_parpadear():
    while not button.value():
        led_avanzar.value(1)
        led_midiendo.value(1)
        led_wifi.value(1)
        time.sleep(0.5)
        led_avanzar.value(0)
        led_midiendo.value(0)
        led_wifi.value(0)
        time.sleep(0.5)

def main():
    if not connect_wifi():
        return
    
    global distance
    distance = 1
    
    while distance <= 5:
        if not button.value():
            display_measurement_start()
            leds_parpadear()
            rssi_values, rssi_average, stddev_rssi = measure_rssi(distance)
            if rssi_values:
                display_rssi(rssi_average, distance)
                display_measurement_done()
                time.sleep(5)
                distance += 1  # Incrementar la distancia y mostrar en OLED
                oled.fill(0)
                oled.text(f"Nueva Dist: {distance}m", 2, 6)
                oled.show()
        time.sleep(0.1)

main()