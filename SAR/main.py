#!/usr/bin/env python3
from ev3dev2.motor import MoveSteering, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor import INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from ev3dev2.sound import Sound
import time
import json 

# --- Configuration ---
LEFT_MOTOR = OUTPUT_B
RIGHT_MOTOR = OUTPUT_A
MEDIUM_MOTOR = OUTPUT_C

# Initialize Hardware
steer_drive = MoveSteering(LEFT_MOTOR, RIGHT_MOTOR)
arm_motor = MediumMotor(MEDIUM_MOTOR)
color_sensor = ColorSensor(INPUT_2)
us_sensor = UltrasonicSensor(INPUT_3)
sound = Sound()

# Global Constants
DEFAULT_SPEED = 15
TARGET_LIGHT = 60
# --- NEW: Dashboard State ---
victim_count = 0

def update_dashboard(status_message):
    global victim_count
    data = {
        "victims": victim_count,
        "status": status_message,
        "timestamp": time.time()
    }
    with open('dashboard_data.json', 'w') as f:
        json.dump(data, f)

def obstacle():
    """Obstacle avoidance with smooth arcs"""
    update_dashboard("Avoiding Obstacle")
    # Reverse slightly
    steer_drive.on_for_rotations(steering=0, speed=-15, rotations=0.5)
    
    # Smooth Left Arc (Steering -30 is already good for this)
    steer_drive.on_for_rotations(steering=-30, speed=DEFAULT_SPEED, rotations=1.3)
    
    # Smooth Right Arc
    steer_drive.on_for_rotations(steering=30, speed=DEFAULT_SPEED, rotations=1.3)
    
    # Return to line
    steer_drive.on_for_rotations(steering=0, speed=DEFAULT_SPEED, rotations=0.5)
    steer_drive.on_for_rotations(steering=20, speed=DEFAULT_SPEED, rotations=1.6)
    
    # Wait for line
    steer_drive.on(steering=0, speed=DEFAULT_SPEED)
    while color_sensor.reflected_light_intensity >= 50:
        time.sleep(0.01)
    steer_drive.off()
    update_dashboard("Searching...")

def red_victim():
    """Handles Red Victim rescue with SMOOTH CIRCLE turn"""
    global victim_count
    update_dashboard("Rescuing Red Victim!")
    steer_drive.off()
    
    # 1. Grab Victim
    arm_motor.on_for_rotations(speed=30, rotations=3)
    arm_motor.on_for_rotations(speed=30, rotations=-3)
    
    victim_count += 1
    update_dashboard("Victim Secured (Total: {})".format(victim_count))
    
    # 2. Back up straight
    steer_drive.on_for_rotations(steering=0, speed=-15, rotations=1)
    
    # 3. THE FIX: Small Circle Turn (U-Turn)
    # steering=-60 creates a tight arc. 
    # rotations=2.6 is a guess for 180 degrees. Tweak this if it turns too much/little.
    steer_drive.on_for_rotations(steering=-60, speed=15, rotations=2.6)
    
    # 4. Drive back to line
    steer_drive.on(steering=0, speed=15)
    while color_sensor.reflected_light_intensity >= 50:
        time.sleep(0.01)
    steer_drive.off()

def green_victim():
    """Handles Green Victim rescue with SMOOTH CIRCLE turn"""
    global victim_count
    update_dashboard("Rescuing Green Victim!")
    steer_drive.off()
    
    # 1. Grab Victim
    arm_motor.on_for_rotations(speed=30, rotations=3)
    arm_motor.on_for_rotations(speed=30, rotations=-3)
    
    victim_count += 1
    update_dashboard("Victim Secured (Total: {})".format(victim_count))
    
    # 2. THE FIX: Small Circle Turn (U-Turn)
    # Since Green is usually on the side, we might need a slightly different arc.
    # Trying the same logic as Red for consistency.
    steer_drive.on_for_rotations(steering=-60, speed=15, rotations=2.5)
    
    # 3. Drive back to line
    steer_drive.on(steering=0, speed=15)
    while color_sensor.reflected_light_intensity >= 50:
        time.sleep(0.01)
    steer_drive.off()

def line_follow():
    current_light = color_sensor.reflected_light_intensity
    error = current_light - TARGET_LIGHT

    # Steering (same as before)
    turn = error * 1.5
    turn = max(min(turn, 100), -100)

    # 🔹 Adaptive speed (Fix 1)
    speed = DEFAULT_SPEED
    if abs(turn) > 60:          # very sharp turn
        speed = 8
    elif abs(turn) > 40:        # medium turn
        speed = 12

    steer_drive.on(steering=turn, speed=speed)


# --- Main Program ---
def main():
    sound.speak("System Ready")
    update_dashboard("Mission Started")
    time.sleep(5)
    
    while True:
        if us_sensor.distance_centimeters < 15:
            obstacle()
        elif color_sensor.color == ColorSensor.COLOR_RED:
            red_victim()
        elif (16 < color_sensor.reflected_light_intensity < 23) and \
             (color_sensor.color == ColorSensor.COLOR_GREEN):
            green_victim()
        else:
            line_follow()

if __name__ == '__main__':
    main()