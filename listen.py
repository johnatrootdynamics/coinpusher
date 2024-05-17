import RPi.GPIO as GPIO
import time

def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 21 as input
    GPIO.setup(17, GPIO.OUT)  # Set GPIO 17 as output for the relay

def main():
    count = 0
    setup_gpio()
    try:
        while True:
            if GPIO.input(21) == GPIO.HIGH:
                GPIO.output(17, GPIO.HIGH)  # Turn on relay
                count + 1
                print("Relay ON")
                print(count)
            else:
                GPIO.output(17, GPIO.LOW)  # Turn off relay
                print("Relay OFF")
            time.sleep(0.1)  # Sleep for 100 milliseconds

    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        GPIO.cleanup()  # Ensure GPIOs are reset on exit

if __name__ == "__main__":
    main()
