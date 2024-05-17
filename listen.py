import RPi.GPIO as GPIO
import time

def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Set the pin numbering system to BCM
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 27 as input with a pull-down resistor

def print_tickets(channel):
    if GPIO.input(channel) == GPIO.HIGH:
        print("Printing tickets")

def main():
    try:
        setup_gpio()
        GPIO.add_event_detect(21, GPIO.RISING, callback=print_tickets, bouncetime=200)
        while True:
            time.sleep(1)  # Keep the script running to monitor the GPIO input
    except KeyboardInterrupt:
        print("Program stopped")
    except RuntimeError as e:
        print("Runtime error:", e)
    finally:
        GPIO.cleanup()  # Clean up GPIO settings

if __name__ == "__main__":
    main()
