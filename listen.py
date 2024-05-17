import RPi.GPIO as GPIO
import time

def setup_gpio():
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set GPIO 21 as input
    GPIO.setup(17, GPIO.OUT)  # Set GPIO 17 as output for the relay

def main():
    setup_gpio()
    count = 0  # Initialize the counter to 0

    try:
        while True:
            if GPIO.input(21) == GPIO.HIGH:
                GPIO.output(17, GPIO.HIGH)  # Turn on relay
                count += 1  # Increment count when relay is on
                print("Relay ON, Count:", count)
                time.sleep(.1)
                GPIO.output(17, GPIO.LOW)
            else:
                if count > 0:  # Only print when there was a previous count
                    print("Final count before relay off:", count)
                  # Turn off relay
                count = 0  # Reset count when relay is off
                print("Relay OFF")
            time.sleep(0.1)  # Sleep for 100 milliseconds

    except KeyboardInterrupt:
        print("Program terminated by user")
    finally:
        GPIO.cleanup()  # Ensure GPIOs are reset on exit

if __name__ == "__main__":
    main()
