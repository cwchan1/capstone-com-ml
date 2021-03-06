### Library Imports
import adafruit_ccs811          # Air Sensor Library
import adafruit_mpl3115a2       # Pressure Sensor Library
import time
import busio                    # For I2C data busio
import board
import serial
import adafruit_vc0706          # Camera library
import Adafruit_DHT             # Humidity/Temperature sensor
import gpiozero                 # SPI and Digital I/O

import database_constants

class Sensors():
    ### Constant definitions
    ## I2C (Air Quality and Pressure Sensor)
    PRES_SENS_ADDRESS = 0x60
    AIRQ_SENS_ADDRESS = 0x5b
    SEA_LEVEL_PRES = 101325         # Sea level pressure [Pa]

    ## UART (Camera)
    UART_BAUD_RATE = 115200
    UART_TIMEOUT = 1                # Timeout for the UART [s]
    UART_PORT = "/dev/ttyS0"
    IMAGE_FILE = '/home/pi/PVCT/image.jpg'      # Full path to file name to save image from camera. Will overwrite!

    ## Ultrasonic Sensor
    ULTRA_ECHO_PIN_NUM = 21
    ULTRA_TRIG_PIN_NUM = 20
    RESP_WAIT_TIMEOUT = 1           # Maximum time to wait for a response from the ultrasonic sensor [s]
    ECHO_WAIT_TIMEOUT = 1           # Maximum time that echo pin should be held high [s]
    TRIG_TIME = 0.00001             # Time to trigger a reading from the sensor (10 us) [s]
    DIST_CONV_FACTOR = 1000000 / 58 # Converts time from seconds to distance in centimeters
    WAIT_BETWEEN_READ = 0.5         # Time between distance readings [s]
    ULTRA_READINGS = 5              # Number of readings per loop (should be 3 minimum)
    MIN_VALID_READINGS = 3          # Minimum number of valid readings per loop

    ## Humidity Sensor
    HUMID_PIN_NUM = 12

    ## SPI ADC Sensors (Irradiance, Power, Surface Temperature)
    SOLAR_IRRAD_SEL_PIN_NUM = 19
    POWER_OUT_SEL_PIN_NUM = 26

    ## Other Constants
    INIT_WAIT_TIME = 3              # Wait time after configuration

    def __init__(self):
        ### Configuration
        print('Configuration has begun.')

        ## I2C setup (Air quality and pressure sensors)
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.ccs811 = adafruit_ccs811.CCS811(self.i2c_bus, Sensors.AIRQ_SENS_ADDRESS)
        self.presSensor = adafruit_mpl3115a2.MPL3115A2(self.i2c_bus, address=Sensors.PRES_SENS_ADDRESS)
        self.presSensor.sealevel_pressure = Sensors.SEA_LEVEL_PRES
        print('I2C has been configured.')

        ## Camera setup
        print('Configuring the camera.')
        # Setup the UART 
        self.uart = serial.Serial(Sensors.UART_PORT, baudrate=Sensors.UART_BAUD_RATE, timeout=Sensors.UART_TIMEOUT)

        # Setup VC0706 camera
        self.vc0706 = adafruit_vc0706.VC0706(self.uart)
        
        # Print the version string from the camera.
        print('VC0706 version:')
        print(self.vc0706.version)
        
        # Set the image size.
        self.vc0706.image_size = adafruit_vc0706.IMAGE_SIZE_640x480
        
        # Note you can also read the property and compare against those values to see the current size:
        imageSize = self.vc0706.image_size
        if imageSize == adafruit_vc0706.IMAGE_SIZE_640x480:
            print('Using 640x480 size image.')
        elif imageSize == adafruit_vc0706.IMAGE_SIZE_320x240:
            print('Using 320x240 size image.')
        elif imageSize == adafruit_vc0706.IMAGE_SIZE_160x120:
            print('Using 160x120 size image.')
        print('Camera has been configured.')
            
        ## Ultrasonic sensor setup
        self.echoPin = gpiozero.DigitalInputDevice(Sensors.ULTRA_ECHO_PIN_NUM)
        self.trigPin = gpiozero.DigitalOutputDevice(Sensors.ULTRA_TRIG_PIN_NUM)

        self.trigPin.off()
        print('Ultrasonic sensor has been configured.')

        ## Humidity sensor setup
        self.humidSensor = Adafruit_DHT.DHT22
        self.humidPin = Sensors.HUMID_PIN_NUM
        print('Humidity sensor has been configured.')

        ## SPI setup
        # Sets up MCP3202 ADCs
        self.solarIrradADC = gpiozero.MCP3202(channel=0, differential=True, select_pin=Sensors.SOLAR_IRRAD_SEL_PIN_NUM)
        self.powerOutADC = gpiozero.MCP3202(channel=0, differential=True, select_pin=Sensors.POWER_OUT_SEL_PIN_NUM)
        self.surfTempADC0 = gpiozero.MCP3208(channel=0, differential=False, select_pin=13)
        self.surfTempADC1 = gpiozero.MCP3208(channel=1, differential=False, select_pin=13)
        self.surfTempADC2 = gpiozero.MCP3208(channel=2, differential=False, select_pin=13)
        self.surfTempADC3 = gpiozero.MCP3208(channel=3, differential=False, select_pin=13)
        self.surfTempADC4 = gpiozero.MCP3208(channel=4, differential=False, select_pin=13)
        self.surfTempADC5 = gpiozero.MCP3208(channel=5, differential=False, select_pin=13)
        print('SPI ADCs have been configured.')

        ######### Need code for MCP3208 ADCs 


        ## Wait for the AQ sensor to be ready, then wait another few seconds for things to settle
        print('Waiting for sensors to be ready.')
        while not self.ccs811.data_ready:
            pass
        time.sleep(Sensors.INIT_WAIT_TIME)
        print('Sensors ready. Real time loop beginning.')
        print('------------------------------------------------\n')


    ### Function definitions
    def ultrasonic_dist_read(self):
        """This function returns the distance reading from the ultrasonic sensor
        in cm or -1 if there is an error in the reading"""

        ultrasonicFail = False            # Used to track if there is no response from the sensor
        
        # Trigger a reading from the sensor
        self.trigPin.on()
        time.sleep(Sensors.TRIG_TIME)
        self.trigPin.off()
        
        # Wait for a response
        waitStartTime = time.time()
        while self.echoPin.value == 0:
            # Times out if there is no response for too long
            if (time.time() - waitStartTime) > Sensors.RESP_WAIT_TIMEOUT:
                print('No Response from the Ultrasonic Sensor.')
                ultrasonicFail = True
                break
        
        # Measure length of the response
        if (not(ultrasonicFail)):
            echoStartTime = time.time()
            while self.echoPin.value == 1:
                if (time.time() - echoStartTime) > Sensors.ECHO_WAIT_TIMEOUT:
                    break
            
            # Calculates the distance measured from echo time
            echoLength = time.time() - echoStartTime
            ultraDistance = echoLength * Sensors.DIST_CONV_FACTOR
            
        # Returns appropriate distance
        if (ultrasonicFail):
            ultraDistance = -1
        else:
            ultraDistance = echoLength * Sensors.DIST_CONV_FACTOR
        return ultraDistance

    
    ### Real-time loop
    def run(self):
        data_dict = {}

        print('------------------------------------------------\n')
        # Keeps track of time for each loop
        startTime = time.time()

        ## Air quality sensor
        co2Conc = self.ccs811.eco2               # CO2 concentration reading [PPM]
        tvocConc = self.ccs811.tvoc              # TVOC concentration reading [PPB]
        print("CO2: {} PPM, TVOC: {} PPB".format(self.ccs811.eco2, self.ccs811.tvoc))

        data_dict[database_constants.CONST_CARBON_DIOXIDE] = co2Conc
        data_dict[database_constants.CONST_TVOC] = tvocConc
        
        ## Pressure/Altitude sensor
        pressure = self.presSensor.pressure          # Presure sensor reading [Pa]
        print("P: ", pressure, " Pa")        
        altitude = self.presSensor.altitude          # Altitude sensor reading [m]
        print("A: ", altitude, " m")
        presTemp = self.presSensor.temperature       # Temperature reading [degC]
        print("T: ", presTemp, " degC")

        data_dict[database_constants.CONST_PRESSURE] = pressure
        data_dict[database_constants.CONST_TEMPERATURE] = presTemp
        
        ## Ultrasonic sensor
        # Takes several readings and puts them in an array
        ultraDistanceArray = []
        for ultraReading in range(Sensors.ULTRA_READINGS):
            time.sleep(Sensors.WAIT_BETWEEN_READ)
            ultraDistanceArray.append(self.ultrasonic_dist_read())
        
        # Removes error readings of -1, or submits -1 as the distance if there are less than 3 valid readings
        if ((Sensors.ULTRA_READINGS - ultraDistanceArray.count(-1)) >= Sensors.MIN_VALID_READINGS):
            # Removes max and min readings
            ultraDistanceArray.remove(max(ultraDistanceArray))
            ultraDistanceArray.remove(min(ultraDistanceArray))
            
            # Takes average for result
            ultraDistance = sum(ultraDistanceArray) / len(ultraDistanceArray)
        else:
            # Error code -1
            ultraDistance = -1

        if (ultraDistance > 0):
            print("Distance is:", ultraDistance, " cm")
        else:
            print("Error with Ultrasonic Sensor Reading.")

        data_dict[database_constants.CONST_DISTANCE] = ultraDistance

        ## Humidity sensor
        # Takes a reading from the sensor
        (humidity, humidTemp) = Adafruit_DHT.read_retry(self.humidSensor, self.humidPin)
        if humidity is not None and humidTemp is not None:
            print("Temp: ", humidTemp, " degC")
            print("Humid: ", humidity, "%")
        else:
            print("Failed to get reading. Try again!")

        data_dict[database_constants.CONST_HUMIDITY] = humidity
            
        ## SPI ADCs
        print("Solar Irradiance ADC Reading: " + str(self.solarIrradADC.value * 3.3) + " V")
        print("Power Out ADC Reading: " + str(self.powerOutADC.value * 3.3) + " V")
        print("Surface Temperature 0 Reading: " + str(((self.surfTempADC0.value * 3300) - 500) / 10) + " degC")
        print("Surface Temperature 1 Reading: " + str(((self.surfTempADC1.value * 3300) - 500) / 10) + " degC")
        print("Surface Temperature 2 Reading: " + str(((self.surfTempADC2.value * 3300) - 500) / 10) + " degC")
        print("Surface Temperature 3 Reading: " + str(((self.surfTempADC3.value * 3300) - 500) / 10) + " degC")
        print("Surface Temperature 4 Reading: " + str(((self.surfTempADC4.value * 3300) - 500) / 10) + " degC")
        print("Surface Temperature 5 Reading: " + str(((self.surfTempADC5.value * 3300) - 500) / 10) + " degC")

        #data_dict[database_constants.CONST_POWER_OUTPUT] = self.solarIrradADC.value
        data_dict[database_constants.CONST_POWER_OUTPUT] = self.powerOutADC.value
        data_dict[database_constants.CONST_POWER_OUTPUT] = self.surfTempADC0.value
        data_dict[database_constants.CONST_PANEL_TEMPERATURE_ONE] = self.surfTempADC0.value
        data_dict[database_constants.CONST_PANEL_TEMPERATURE_TWO] = self.surfTempADC1.value
        data_dict[database_constants.CONST_PANEL_TEMPERATURE_THREE] = self.surfTempADC2.value
        data_dict[database_constants.CONST_PANEL_TEMPERATURE_FOUR] = self.surfTempADC3.value
        data_dict[database_constants.CONST_PANEL_TEMPERATURE_FIVE] = self.surfTempADC4.value
        data_dict[database_constants.CONST_PANEL_TEMPERATURE_SIX] = self.surfTempADC5.value
        ######### Need code for MCP3208 ADCs 
    
        ## Camera
        # Take a picture
        print('Taking a picture.')
        if not self.vc0706.take_picture():
            raise RuntimeError('Failed to take picture!')
        
        # Print size of picture in bytes.
        frame_length = self.vc0706.frame_length
        print('Picture size (bytes): {}'.format(frame_length))
        
        # Open a file for writing (overwriting it if necessary).
        # This will write 50 bytes at a time using a small buffer.
        # You MUST keep the buffer size under 100!
        print('Writing image: {}'.format(Sensors.IMAGE_FILE), end='', flush=True)
        stamp = time.monotonic()
        with open(Sensors.IMAGE_FILE, 'wb') as outfile:
            wcount = 0
            while frame_length > 0:
                t = time.monotonic()
                # Compute how much data is left to read as the lesser of remaining bytes
                # or the copy buffer size (32 bytes at a time).  Buffer size MUST be
                # a multiple of 4 and under 100.  Stick with 32!
                to_read = min(frame_length, 32)
                copy_buffer = bytearray(to_read)
                # Read picture data into the copy buffer.
                if self.vc0706.read_picture_into(copy_buffer) == 0:
                    raise RuntimeError('Failed to read picture frame data!')
                # Write the data to SD card file and decrement remaining bytes.
                outfile.write(copy_buffer)
                frame_length -= 32
                # Print a dot every 2k bytes to show progress.
                wcount += 1
                if wcount >= 64:
                    print('.', end='', flush=True)
                    wcount = 0
        print()
        print('Finished taking picture in %0.1f seconds!' % (time.monotonic() - stamp))
        
        print("Real time loop complete in ", time.time() - startTime, " seconds.")
        print('------------------------------------------------\n')

        return data_dict
