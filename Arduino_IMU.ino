#include "Arduino_BMI270_BMM150.h"

float gx, gy, gz, ax, ay, az;  // Raw gyro and accelerometer data

void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("Started");

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  Serial.println("IMU Initialized");
}

void resetIMU() {
  // Reinitialize the IMU to reset internal states
  if (!IMU.begin()) {
    Serial.println("Failed to reinitialize IMU!");
  } else {
    Serial.println("IMU Reset Complete");
  }
}

void loop() {
  // responding to reset ('R') command from python if needed:
  if (Serial.available()) {
    char command = Serial.read();
    if (command == 'R') {
      resetIMU();  // Reset IMU if 'R' command is received
      // return;  // use if I want to Skip the rest of the loop this cycle
    }
  }

  // Read raw gyroscope data
  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(gx, gy, gz);
  }

  // Read raw accelerometer data
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(ax, ay, az);
  }

  // Send raw data to the serial monitor
  Serial.print(gx);
  Serial.print("\t");
  Serial.print(gy);
  Serial.print("\t");
  Serial.print(gz);
  Serial.print("\t");
  Serial.print(ax);
  Serial.print("\t");
  Serial.print(ay); 
  Serial.print("\t");
  Serial.println(az);  

}
