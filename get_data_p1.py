# ISKRA P1 reader
# (c) 11-2017 2016 - GJ - gratis te kopieren en te plakken
# Version 2.0: MH KOK updates for P1 to S3

version = "2.0"
import sys
import serial
import json
import datetime
import boto3 
import os 
from dotenv import load_dotenv

stack = []

def show_error():
    """
    Error display
    """
    ft = sys.exc_info()[0]
    fv = sys.exc_info()[1]
    print("Fout type: %s" % ft )
    print("Fout waarde: %s" % fv )
    return


def read_p1_output():
    """
    This function reads the output of P1 output from smartmeter
    """
    print ("DSMR 5.0 P1 reader",  version)
    print ("Control-C om te stoppen")

    #Set COM port config
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.xonxoff=0
    ser.rtscts=0
    ser.timeout=20
    ser.port="/dev/ttyUSB0"

    #Open COM port
    try:
        ser.open()
    except:
        sys.exit ("Fout bij het openen van %s. Programma afgebroken."  % ser.name)


    # Initialize
    # Stack is list for reading P1 output
    p1_counter=0
    
    while p1_counter < 26:
        p1_line=''
        #Read 1 line
        try:
            p1_raw = ser.readline()
            #print (p1_raw)
        except:
            sys.exit ("Seriele poort %s kan niet gelezen worden. Programma afgebroken." % ser.name )
        p1_str=str(p1_raw)
        p1_line=p1_str.strip()
        stack.append(p1_line)
        #print (p1_line)
        #print (stack)
        p1_counter = p1_counter +1
        
        #try:
        #    ser.close()
    
        #except:
        #    sys.exit ("Oops %s. Programma afgebroken." % ser.name )

    return stack

def create_json(usage_dict):
    global fileName
    now = datetime.datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M")
    fileName = "p1_raw_data_" + dt_string + ".json"

    with open(fileName, "w") as f:
      json.dump(usage_dict, f)
      
    return fileName

def copy_s3(fileName):
    print (fileName)
    load_dotenv() # this loads the .env file with our credentials

    file_name = fileName # name of the file to upload
    bucket_name = 'p1-staging' # name of the bucket

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    response = s3_client.upload_file(file_name, bucket_name, file_name)
    print (response)
    
    return


def process_p1_output(stack):
    stack_teller=0
    #meter=0
    global usage_dict

    while stack_teller < 26:
        if stack[stack_teller][0:9] == "1-0:1.8.1":
            off_peak_hours_usage = float(stack[stack_teller][10:20])
            off_peak_hours_key = stack[stack_teller][0:9]
            print ("off_peak_hours: ") + stack[stack_teller][10:20]
        elif stack[stack_teller][0:9] == "1-0:1.8.2":      
            peak_hours_usage = float(stack[stack_teller][10:20])
            peak_hours_key = stack[stack_teller][0:9]
            print ("peak_hours: ") + stack[stack_teller][10:20]
        # Off peak hours, teruggeleverd vermogen 1-0:2.8.1
        elif stack[stack_teller][0:9] == "1-0:2.8.1":
            off_peak_hours_returned = float(stack[stack_teller][10:20])
            off_peak_hours_returned_key = stack[stack_teller][0:9]
            print ("off_peak_hours_returned: ") + stack[stack_teller][10:20]
        ## Peak hours, teruggeleverd vermogen 1-0:2.8.2
        elif stack[stack_teller][0:9] == "1-0:2.8.2":
            peak_hours_returned = float(stack[stack_teller][10:20])
            peak_hours_returned_key = stack[stack_teller][0:9]
            print ("peak_hours_returned: ") + stack[stack_teller][10:20]
        ## Current power usage: 1-0:1.7.0
        elif stack[stack_teller][0:9] == "1-0:1.7.0":
            current_power_usage = float(stack[stack_teller][10:16])
            current_power_usage_key = stack[stack_teller][0:9]
            print ("current_power_usage: ") + stack[stack_teller][10:16]
        ## Current power returned: 1-0:1.7.0
        elif stack[stack_teller][0:9] == "1-0:2.7.0":
            current_power_returned = float(stack[stack_teller][10:16])
            current_power_usage_returned_key = stack[stack_teller][0:9]
            print ("current_power_usage_returned: ") + stack[stack_teller][10:16]
        # Gas meterage: 0-1:24.2.1
        elif stack[stack_teller][0:10] == "0-1:24.2.1":
                gas_usage = float(stack[stack_teller][26:35])
                gas_usage_key = stack[stack_teller][0:10]
                print ("gas_usage: ") + stack[stack_teller][26:35]
        else:
            pass
        stack_teller = stack_teller +1

    # Debug
    #print (stack, "\n")
    
    data = [off_peak_hours_usage, peak_hours_usage, off_peak_hours_returned, peak_hours_returned, current_power_usage, current_power_returned, gas_usage]
    #print (data)
    data_key = ["off_peak_hours_kwh", "peak_hours_kwh", "off_peak_hours_returned_kwh", "peak_hours_returned_kwh", "current_power_usage_kwh", "current_power_returned_kwh", "gas_usage_m3"]
    
    usage_dict = dict(zip(data_key, data))

    print(usage_dict)

    #Close port and show status
    return usage_dict 


def main():
    """
    This function invokes the following functions:
    - read P1 output
    - create JSON file
    """
    read_p1_output()
    process_p1_output(stack)
    create_json(usage_dict)
    copy_s3(fileName)
    
if __name__ == "__main__":
    main()



