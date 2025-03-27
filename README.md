# Viral-Vengeance
Python Game "Viral Vengeance" for Arduino_BMI270_BMM150 IMU as controller.

Arduino_IMU is used to process imu data. Use this to first check arduino is connected. Close out of serial monitor (or entire IDE application) before running game in python.

FilteringOnPython pulls the gyroscope and accelerometer data from the serial port. Adjust for correct port and Mac vs Windows users.

Viral_Vengeance code is used to play the game. Once you run the code, it will pull the filtered data from FilteringOnPython, and bring up the game in a user monitor. Python codes were developed and ran using VSCode.

Assets folder must be downloaded for the graphics of the game. Also ensure all packages are installed before running game.


