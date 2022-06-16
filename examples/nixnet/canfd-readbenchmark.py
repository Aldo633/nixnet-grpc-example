r""" CANFD Raw Frame Loopback.

 This example reads and writes raw CAN FD frames through two different interfaces
 This is used to demonstrate read and write sessions without a databases
 This example uses a hardcoded frame ID .
 You can modify the ID and payload on the fly by modifying their values
 Also ensure that the transceivers are externally powered when using C Series modules.

The gRPC API is built from the C API. NI-XNET documentation is installed with the driver at:
  C:\Users\Public\Documents\National Instruments\NI-XNET\Documentation\NI-XNET Manual.chm
Getting Started:

To run this example, install "NI-XNET Driver" on the server machine:
  https://www.ni.com/en-in/support/downloads/drivers/download.ni-xnet.html

For instructions on how to use protoc to generate gRPC client interfaces, see our "Creating a gRPC
Client" wiki page:
  https://github.com/ni/grpc-device/wiki/Creating-a-gRPC-Client

Refer to the NI XNET gRPC Wiki for the latest C Function Reference:
  https://github.com/ni/grpc-device/wiki/NI-XNET-C-Function-Reference

Running from command line:
Server machine's IP address, port number, and interface name can be passed as separate command line
arguments.
  > python canfd-raw-loopback.py <server_address> <port_number> <interface_name1> <interface_name2>
If they are not passed in as command line arguments, then by default the server address will be
"localhost:31763"
"""

import sys
import time
import grpc
from numpy import uint64
import nixnet_pb2 as nixnet_types
import nixnet_pb2_grpc as grpc_nixnet
import time

SERVER_ADDRESS = "localhost"
SERVER_PORT = "31763"
INTERFACE1 = "CAN1"
INTERFACE2 = "CAN2"

# Read in cmd args
if len(sys.argv) >= 2:
    SERVER_ADDRESS = sys.argv[1]
if len(sys.argv) >= 3:
    SERVER_PORT = sys.argv[2]
if len(sys.argv) >= 4:
    INTERFACE1 = sys.argv[3]
if len(sys.argv) >= 5:
    INTERFACE2 = sys.argv[4]

# Parameters
DATABASE = ":can_fd_brs:" #constant to define FD-BRS communication. You can use :memory: to use CAN 2.0 instead, or use :can_fd: to configure CAN FD without Bit Rate Switching
CLUSTER = ""
CAN_EXTENDED_ID_FLAG =0x20000000 
CAN_IDENTIFIER = 0x124524 |CAN_EXTENDED_ID_FLAG #setting up CAN ID to transmit, use the Extended ID flag if configuring 29 bit IDs
NUMBER_OF_FRAMES = 1



def check_for_error(status):
    """Raise an exception if the status indicates an error."""
    if status != 0:
        error_message_response = client.StatusToString(
            nixnet_types.StatusToStringRequest(status_id=status)
        )
        raise Exception(error_message_response.status_description)


i = 0
#define frames
payload_list = [0x7F, 0x3F] *6
canfdframe=nixnet_types.FrameRequest(identifier=CAN_IDENTIFIER, type = nixnet_types.FRAME_TYPE_CANFDBRS_DATA, payload= bytes(payload_list))
canfdframes=[nixnet_types.FrameBufferRequest(can= canfdframe)]

session_tx = None
session_rx = None

# Create the communication channel for the remote host and create connections to the NI-XNET and
# session services.
channel = grpc.insecure_channel(f"{SERVER_ADDRESS}:{SERVER_PORT}")
client = grpc_nixnet.NiXnetStub(channel)

# Display parameters that will be used for the example.
print("Interface: " + INTERFACE1, "Database: " + DATABASE, sep="\n")

try:
    # Create an Output Session
    create_session_response = client.CreateSession(
        nixnet_types.CreateSessionRequest(
            database_name=DATABASE,
            cluster_name=CLUSTER,
            interface_name=INTERFACE1,
            mode=nixnet_types.CREATE_SESSION_MODE_FRAME_OUT_STREAM,
        )
    )
    check_for_error(create_session_response.status)
    session_tx = create_session_response.session

    #Create an Input Session
    create_session_response = client.CreateSession(
        nixnet_types.CreateSessionRequest(
            database_name = DATABASE,
            interface_name =INTERFACE2,
            mode = nixnet_types.CREATE_SESSION_MODE_FRAME_IN_STREAM,
        )
    )
    check_for_error(create_session_response.status)
    session_rx = create_session_response.session

    print("session" +str(session_rx))
    print("Sessions Created Successfully.\n")

    
    #Set TX Session Properties
    #Set CAN Header Data Rate
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session_tx,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_BAUD_RATE_64,
            u64_scalar=1000000,
        )
    )
    check_for_error(set_property_response.status)

    #Set Message FD Data Rate
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session_tx,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_CAN_FD_BAUD_RATE_64,
            u64_scalar=1000000,
        )
    )
    check_for_error(set_property_response.status)

       #Set Termination
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session_tx,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_CAN_TERM,
            u32_scalar=nixnet_types.PROPERTY_VALUE_CAN_TERM_ON,
        )
    )
    check_for_error(set_property_response.status)
       
    
    #Set Rx Session Properties
    #Set CAN Header Data Rate
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session_rx,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_BAUD_RATE_64,
            u64_scalar=1000000,
        )
    )
    check_for_error(set_property_response.status)

    #Set Message FD Data Rate
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session_rx,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_CAN_FD_BAUD_RATE_64,
            u64_scalar=1000000,
        )
    )
    check_for_error(set_property_response.status)


   

    #Set Termination
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session_rx,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_CAN_TERM,
            u32_scalar=nixnet_types.PROPERTY_VALUE_CAN_TERM_ON,
        )
    )
    check_for_error(set_property_response.status)
    
    get_property_response=client.GetProperty(
        nixnet_types.GetPropertyRequest(
            session = session_rx,
            property_id = nixnet_types.PROPERTY_SESSION_INTF_CAN_TERM,
        )
    )
    check_for_error(get_property_response.status)
    print("Termination Property Value: " +str(get_property_response.u32_scalar))


    #Start Read Session 
    start_response = client.Start(
        nixnet_types.StartRequest(
            session = session_rx,
            scope = nixnet_types.START_STOP_SCOPE_NORMAL
        )
    )
    check_for_error(start_response.status)

    
    print("Writing 10 frames to CAN Interface.\n")
    while i < 10000:
         

        
        # Update the frame data
        
        write_frame_response = client.WriteFrame(
            nixnet_types.WriteFrameRequest(session=session_tx, buffer=canfdframes, timeout = nixnet_types.TIME_OUT_NONE)
        )
        check_for_error(write_frame_response.status)

        print("Frame sent:")
        
        start_time = time.time()
        
        read_frame_response = client.ReadFrame(
            nixnet_types.ReadFrameRequest(
                session=session_rx,
                number_of_frames = NUMBER_OF_FRAMES,
                max_payload_per_frame = len(payload_list),
                protocol = nixnet_types.PROTOCOL_CAN,
                timeout = nixnet_types.TIME_OUT_NONE
            )
        )
        stop_time = time.time()
        elapsed_time = (stop_time - start_time)
        
        #check_for_error(write_frame_response.status)
        frame_buffer = read_frame_response.buffer

        if(elapsed_time>0.005):
            print("Iteration: ", i,"/nElapsed time: ",elapsed_time)
        #print("Frame received:"+"ID = "+str(frame_buffer[0].can.identifier))
        for j in range (0,len(frame_buffer)):
            #print("Payload " + str(frame_buffer[j].can.payload)+ "\n")
            #Print out frames received
            for k in range(0,len(frame_buffer[j].can.payload)):
                print(
                    "{:02x}".format(int(frame_buffer[j].can.payload[k])).upper(),
                    end=" ",
                )
            print("\n\n")
      
        i = i + 1

except grpc.RpcError as rpc_error:
    error_message = rpc_error.details()
    if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
        error_message = f"Failed to connect to server on {SERVER_ADDRESS}:{SERVER_PORT}"
    elif rpc_error.code() == grpc.StatusCode.UNIMPLEMENTED:
        error_message = (
            "The operation is not implemented or is not supported/enabled in this service"
        )
    print(f"{error_message}")

finally:
    if session_tx:
        # clear the XNET Write session.
        check_for_error(client.Clear(nixnet_types.ClearRequest(session = session_tx)).status)
        print("Tx Session cleared successfully!\n")

    if session_rx:
        # clear the XNET Read session.
        check_for_error(client.Clear(nixnet_types.ClearRequest(session = session_rx)).status)
        print("Rx Session cleared successfully!\n")
