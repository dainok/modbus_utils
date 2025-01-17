#!/usr/bin/env python3

import argparse
import time
from datetime import datetime
from tabulate import tabulate
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
# from pymodbus.exceptions import ConnectionException

REGISTER_TYPES = ["discrete", "coil", "input", "holding"]

if __name__ == "__main__":
    """Main function."""
    started_at = datetime.now()
    
    parser = argparse.ArgumentParser(
		# prog="ProgramName',
		# description='What the program does',
		# epilog='Text at the bottom of help'
	)
    parser.add_argument("-i", "--ip", type=str, required=True, help="PLC IP address")
    parser.add_argument("-p", "--port", type=int, default=502, help="PLC TCP port")
    parser.add_argument("-t", "--type", type=str, required=True, choices=REGISTER_TYPES, help="Register type")
    parser.add_argument("-s", "--start", type=int, default=0, help="The starting address")
    parser.add_argument("-c", "--count", type=int, default=16, help="The number of registers")
    parser.add_argument("-u", "--unit", type=int, default=1, help="The slave unit")
    parser.add_argument("-w", "--wait", type=str, default=1, help="Seconds between requests")
    # parser.print_help()
    args = parser.parse_args()

    # Connect to the PLC
    client = ModbusClient(args.ip, args.port)

    header = ["Time"] + list(range(args.start, args.start + args.count))
    data = []
    print(header)

    try:
        while True:
            now = datetime.now()
            if args.type == "discrete":
                req = client.read_discrete_inputs(args.start, args.count)
                reg = req.bits
            if args.type == "coil":
                req = client.read_coils(args.start, args.count)
                reg = req.bits
            if args.type == "input":
                req = client.read_input_registers(args.start, args.count)
                reg = req.registers
            if args.type == "holding":
                req = client.read_holding_registers(args.start, args.count)
                reg = req.registers
            output = [f"{now.hour}:{now.minute}:{now.second}"] + reg
            data.append(output)
            print(output)
            time.sleep(args.wait)
    except KeyboardInterrupt:
        pass

    # Disconnect from the PLC
    client.close()

    # Calculate min and max
    if args.type in ["input", "holding"]:
        min = ["Min"] + list([None] * (args.count))
        max = ["Max"] + list([None] * (args.count))
        for line in data:
            for i in range(1, args.count + 1):
                if min[i] is None:
                    min[i] = line[i]
                if max[i] is None:
                    max[i] = line[i]
                if line[i] < min[i]:
                    min[i] = line[i]
                if line[i] > max[i]:
                    max[i] = line[i]
        data.append(min)
        data.append(max)

    # Check if registers change
    # if args.type in ["discrete", "coil"]:
    #     change = ["Change?"] + list([False] * (args.count))
    #     for line in data:
    #         for i in range(1, args.count + 1):


    # Display output
    print("\n") # Clear the line
    print(tabulate(data, headers=header))
