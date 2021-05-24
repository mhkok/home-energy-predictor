# ISKRA P1 reader
# (c) 11-2017 2016 - GJ - gratis te kopieren en te plakken
# Version 2.0: MH KOK updates for P1 to S3

version = "2.0"
import sys
import serial
import json
import datetime


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
    stack=[]

    while p1_counter < 26:
        p1_line=''
        #Read 1 line
        try:
            p1_raw = ser.readline()
        # print (p1_raw)
        except:
            sys.exit ("Seriele poort %s kan niet gelezen worden. Programma afgebroken." % ser.name )
        p1_str=str(p1_raw)
        p1_line=p1_str.strip()
        stack.append(p1_line)
    #print (p1_line)
    #print (stack)
    p1_counter = p1_counter +1

    # try:
    # ser.close()
    
    # except:
    # sys.exit ("Oops %s. Programma afgebroken." % ser.name )

    return stack

def create_json(stack):

    currDatetime = datetime.datetime.now()

    with open('p1_raw_data_{}.json'.format(currDatetime), 'w') as f:
        print("The json file is created")

    stackJSON = json.dumps(stack, f, indent=4)
    print(stackJSON)

    return stackJSON


def main():
    """
    This function invokes the following functions:
    - read P1 output
    - create JSON file
    """
    read_p1_output()
    create_json()
    
if __name__ == "__main__":
    main()

#Initialize
# stack_teller is mijn tellertje voor de 26 weer door te lopen. Waarschijnlijk mag ik die p1_teller ook gebruiken
# stack_teller=0
# meter=0

# while stack_teller < 26:
#    if stack[stack_teller][0:9] == "1-0:1.8.1":
#     print "daldag      ", stack[stack_teller][10:23]
#     meter = meter +  int(float(stack[stack_teller][10:16]))
#    elif stack[stack_teller][0:9] == "1-0:1.8.2":
#     print "piekdag     ", stack[stack_teller][10:16]
#     meter = meter + int(float(stack[stack_teller][10:16]))
# #   print "meter totaal   ", meter
# # Daltarief, teruggeleverd vermogen 1-0:2.8.1
#    elif stack[stack_teller][0:9] == "1-0:2.8.1":
#     print "dalterug    ", stack[stack_teller][10:16]
#     meter = meter - int(float(stack[stack_teller][10:16]))
# #   print "meter totaal   ", meter
# # Piek tarief, teruggeleverd vermogen 1-0:2.8.2
#    elif stack[stack_teller][0:9] == "1-0:2.8.2":
#         print "piekterug   ", stack[stack_teller][10:16]
#         meter = meter - int(float(stack[stack_teller][10:16]))
#         print "meter totaal  ", meter, " (afgenomen/teruggeleverd van het net vanaf 01-11-2017)"
# # Huidige stroomafname: 1-0:1.7.0
#    elif stack[stack_teller][0:9] == "1-0:1.7.0":
#         print "Afgenomen vermogen      ", int(float(stack[stack_teller][10:16])), "kW"
# # Huidig teruggeleverd vermogen: 1-0:1.7.0
#    elif stack[stack_teller][0:9] == "1-0:2.7.0":
#         print "Teruggeleverd vermogen  ", int(float(stack[stack_teller][10:16])), "kW"
# # Gasmeter: 0-1:24.2.1
#    elif stack[stack_teller][0:10] == "0-1:24.2.1":
#         print "Gas                     ", int(float(stack[stack_teller][26:35])), "m3"
#    else:
#     pass
#    stack_teller = stack_teller +1

#Debug
#print (stack, "\n")

#Close port and show status
