import RPi.GPIO as GPIO
import time

# Configurar los puertos GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)

try:
    while True:
        # Encender el LED en el puerto 17 y apagar los otros
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(6, GPIO.LOW)
        GPIO.output(5, GPIO.LOW)
        time.sleep(1)
        
        # Encender el LED en el puerto 6 y apagar los otros
        GPIO.output(17, GPIO.LOW)
        GPIO.output(6, GPIO.HIGH)
        GPIO.output(5, GPIO.LOW)
        time.sleep(1)
        
        # Encender el LED en el puerto 5 y apagar los otros
        GPIO.output(17, GPIO.LOW)
        GPIO.output(6, GPIO.LOW)
        GPIO.output(5, GPIO.HIGH)
        time.sleep(1)

except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario.")

finally:
    # Limpiar configuraciones de los puertos GPIO
    GPIO.cleanup()
