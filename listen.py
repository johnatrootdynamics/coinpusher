from gpiozero import Button
from signal import pause

def print_tickets():
    print("Printing tickets")

button = Button(7, pull_up=False)  # Set up GPIO 7 as a button, assuming external pull-down resistor

button.when_pressed = print_tickets

pause()  # This will handle the script running indefinitely