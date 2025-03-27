import serial
import numpy as np
from filterpy.kalman import KalmanFilter
import time

# Configure Serial Port (Update this with the correct port)
#SERIAL_PORT = '/dev/cu.usbmodem141101'
SERIAL_PORT = "COM7"
BAUD_RATE = 115200

# Open Serial Connection
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give Arduino time to initialize
    print("Connected to Arduino!")
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

# Kalman filter initialization function
def initialize_kalman():
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.F = np.array([[1, 0.01], [0, 1]])  # State transition matrix
    kf.H = np.array([[1, 0]])             # Measurement function
    kf.P *= 1000                           # Covariance matrix
    kf.R = 5                               # Measurement noise
    kf.Q = np.array([[0.01, 0], [0, 0.01]]) # Process noise
    return kf

# Initialize Kalman filters
kalmanX = initialize_kalman()
kalmanY = initialize_kalman()
kalmanZ = initialize_kalman()

# Function to compute roll and pitch from accelerometer data
def compute_angles(ax, ay, az):
    roll = np.arctan2(ay, az) * 180 / np.pi
    pitch = np.arctan(-ax / np.sqrt(ay**2 + az**2)) * 180 / np.pi
    return roll, pitch

# Function to send reset command to Arduino
def reset_imu():
    ser.write(b'R')  # Send 'R' command to Arduino
    print("Sent reset command to Arduino")

# Function to read and process IMU data
def process_imu_data():
    try:
        line = ser.readline().decode('utf-8').strip()  # Read and decode line
        if not line:
            return None  # No data received

        data = list(map(float, line.split("\t")))  # Split using tabs
        if len(data) != 6:
            return None  # Skip invalid data

        gx, gy, gz, ax, ay, az = data

        # Compute raw roll and pitch angles from accelerometer
        roll, pitch = compute_angles(ax, ay, az)

        # Apply Kalman filtering
        kalmanX.predict()
        kalmanX.update(roll)
        filtered_roll = kalmanX.x[0]

        kalmanY.predict()
        kalmanY.update(pitch)
        filtered_pitch = kalmanY.x[0]

        kalmanZ.predict()
        kalmanZ.update(gz)  # Estimate yaw using gyroscope Z-axis
        filtered_yaw = kalmanZ.x[0]
        time.sleep(0.001)
        return filtered_roll, filtered_pitch, filtered_yaw  

    except ValueError:
        print("Invalid data received, skipping...")
    except serial.SerialException:
        print("Serial connection lost.")
    except KeyboardInterrupt:
        print("\nUser interrupted, closing serial connection.")
        ser.close()

    return None  # Return None if an exception occurs