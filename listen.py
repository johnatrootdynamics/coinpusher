import RPi.GPIO as GPIO
import time

def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Using Broadcom pin-numbering scheme
    GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 7 as input with a pull-down resistor

def print_tickets(channel):
    if GPIO.input(channel) == GPIO.HIGH:
        print("Printing tickets")

def main():
    setup_gpio()
    GPIO.add_event_detect(7, GPIO.RISING, callback=print_tickets, bouncetime=200)  # Set up edge detection on rising edge

    try:
        while True:
            time.sleep(1)  # Delay to keep the loop
    except KeyboardInterrupt:
        print("Program stopped")
    finally:
        GPIO.cleanup()  # Clean up GPIO on normal exit

if __name__ == "__main__":
    main()
