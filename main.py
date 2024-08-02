from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf, sys
import utime
import dht

button = Pin(21, Pin.IN, Pin.PULL_UP)
button_pressed = False
last_button_time = 0
debounce_time = 50  

led_pins = [4,5,6,7,8,9,10,11,12,13]
n=0
for pin_num in led_pins:
    led_pins[n] = Pin(pin_num, Pin.OUT)
    n+=1

pix_res_x = 128
pix_res_y = 64

sensor = dht.DHT22(Pin(28))

def button_callback(pin):
    global button_pressed, last_button_time
    if utime.ticks_diff(utime.ticks_ms(), last_button_time) > debounce_time:
        button_pressed = True
        last_button_time = utime.ticks_ms()

button.irq(trigger=Pin.IRQ_FALLING, handler=button_callback)

def LedSegOut(array):
    for x in range(10): led_pins[x].value(not(array[x]))

def LedSegPerc(value):
    thresholds=[100,90,80,70,60,50,40,30,20,10]
    array = list(map(lambda x: 1 if x > value else 0, thresholds))
    LedSegOut(array)

def init_i2c(scl_pin, sda_pin):
    i2c_dev = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=200000)
    i2c_addr = [hex(ii) for ii in i2c_dev.scan()]
    
    if not i2c_addr:
        print('No I2C Display Found')
        sys.exit()
    else:
        print("I2C Address      : {}".format(i2c_addr[0]))
        print("I2C Configuration: {}".format(i2c_dev))
    
    return i2c_dev

def display_text(temp, hum):
    oled.fill(0)
    oled.text("Temperature:", 5, 5)
    oled.text(f"{temp:.1f}C", 5, 15)
    oled.text("Humidity:", 5, 35)
    oled.text(f"{hum:.1f}%", 5, 45)
    oled.show()

i2c_dev = init_i2c(scl_pin=3, sda_pin=2)
oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)

def read_sensor():
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        return temp, hum
    except Exception as e:
        print("Error reading sensor:", e)
        return None, None

while True:
    if button_pressed:
        print("power on")
        button_pressed = False
        for i in range(10):
            temp, hum = read_sensor()
            if temp is not None and hum is not None:
                print(f"Temperature: {temp:.1f}C, Humidity: {hum:.1f}%")
                display_text(temp, hum)
                LedSegPerc(hum)
            utime.sleep_ms(500)
    
    temp, hum = read_sensor()
    if hum is not None:
        LedSegPerc(hum)
    oled.fill(0)
    oled.show()
    utime.sleep_ms(100)