import RPi.GPIO as GPIO
import time

def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
    GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 27 as input with a pull-down resistor

def print_tickets(channel):
    if GPIO.input(channel) == GPIO.HIGH:
        print("Printing tickets")

def main():
    setup_gpio()
    # Add a detect event
    GPIO.add_event_detect(27, GPIO.RISING, callback=print_tickets, bouncetime=200)  # Debounce to avoid false triggers

    try:
        while True:
            time.sleep(1)  # Simple delay to keep the script running
    except KeyboardInterrupt:
        print("Program stopped")
    finally:
        GPIO.cleanup()  # Clean up GPIO on normal exit

if __name__ == "__main__":
    main()