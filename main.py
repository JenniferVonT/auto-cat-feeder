from networkSettings import sendTelegramMessage, sendAdafruitData
from servo import ServoClass
from photoSensor import LightSensor
from weightCell import WeightCell
from utime import sleep, time # type: ignore

# Initialize all the classes.
light = LightSensor()
weight = WeightCell()
servo = ServoClass()

# Initialize a variable to track the last time a reminder was sent to the user using Telegram.
lastMessageTime = 0  # Initial value, representing epoch time.

# Define constants.
LOW_LIGHT_THRESHOLD = 51000  # Adjust this threshold as needed.
REFILL_WEIGHT_THRESHOLD = 85  # Adjust this threshold as needed.
HOURS_TO_WAIT = 6 * 3600  # 3600 is seconds per hour so change the first number for the amount of hours.
LOOP_TIME = 10 * 60 # 60 seconds per minute, change the first number to decide the amount of minutes.


while True:
    lightMeasurement = light.measureLight()
    weightMeasurement = weight.getCurrentWeight()
    sendAdafruitData(weightMeasurement - 73)

    ''' # For debugging.
    print("Light measurement: ", lightMeasurement)
    print("Weight measurement:", weightMeasurement)
    '''

    # --------> Check if light is low and it's time to send a message <--------
    if lightMeasurement < LOW_LIGHT_THRESHOLD:
        currentTime = time()

        # Check if enough time has passed since the last message was sent and if a new one should be sent or not.
        if currentTime - lastMessageTime >= HOURS_TO_WAIT:
            sendTelegramMessage("Food is running low! Please refill!")
            lastMessageTime = currentTime  # Update the last message time to delay next time it sends a message (don't spam reminders to often!)

    # --------> Check if weight is low and trigger servo action <--------
    if weightMeasurement <= REFILL_WEIGHT_THRESHOLD:
        tries = 0
        while weightMeasurement <= 150:
            servo.turnValve()
            weightMeasurement = weight.getCurrentWeight()
            print("Weight measurement:", weightMeasurement)
            print("Tries:", tries)
            tries += 1

            # Try 15 times to fill the bowl before alerting that something went wrong.
            if tries == 15:
                sendTelegramMessage("Something went wrong, can't refill bowl!")
                break

            sleep(10) # Try every 10 seconds to fill until the desired weight is reached.

    sleep(LOOP_TIME) # Loop the entire check every X seconds. <-----------------
