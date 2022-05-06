r""" Write Signal Data.

 This example writes a signal value for 10 times.
 This is used to demonstrate a signal single point output session. 
 This example uses hardcoded signal names that use the NIXNET_example database.
 To use your own database, you need to add an alias to your database file using the NI-XNET 
 Database Editor and then modify the database name and signals used here.
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
  > python can-signal-single-point-output.py <server_address> <port_number> <interface_name>
If they are not passed in as command line arguments, then by default the server address will be
"localhost:31763"
"""

import sys

import grpc
from numpy import uint64
import nixnet_pb2 as nixnet_types
import nixnet_pb2_grpc as grpc_nixnet

SERVER_ADDRESS = "localhost"
SERVER_PORT = "31763"
INTERFACE = "CAN1"

# Read in cmd args
if len(sys.argv) >= 2:
    SERVER_ADDRESS = sys.argv[1]
if len(sys.argv) >= 3:
    SERVER_PORT = sys.argv[2]
if len(sys.argv) >= 4:
    INTERFACE = sys.argv[3]

# Parameters
DATABASE = ":can_fd_brs:"
CLUSTER = ""
CAN_EXTENDED_ID_FLAG =0x20000000 
CAN_IDENTIFIER = 0x124524 |CAN_EXTENDED_ID_FLAG



def check_for_error(status):
    """Raise an exception if the status indicates an error."""
    if status != 0:
        error_message_response = client.StatusToString(
            nixnet_types.StatusToStringRequest(status_id=status)
        )
        raise Exception(error_message_response.status_description)


i = 0
#define frames

payload_list = [1] *64
canfdframe=nixnet_types.FrameRequest(identifier=CAN_IDENTIFIER, type = nixnet_types.FRAME_TYPE_CANFDBRS_DATA, payload= bytes(payload_list))
canfdframes=[nixnet_types.FrameBufferRequest(can= canfdframe)]

session = None

# Create the communication channel for the remote host and create connections to the NI-XNET and
# session services.
channel = grpc.insecure_channel(f"{SERVER_ADDRESS}:{SERVER_PORT}")
client = grpc_nixnet.NiXnetStub(channel)

# Display parameters that will be used for the example.
print("Interface: " + INTERFACE, "Database: " + DATABASE, sep="\n")

try:
    # Create an XNET session in FrameOutStream mode
    create_session_response = client.CreateSession(
        nixnet_types.CreateSessionRequest(
            database_name=DATABASE,
            cluster_name=CLUSTER,
            interface_name=INTERFACE,
            mode=nixnet_types.CREATE_SESSION_MODE_FRAME_OUT_STREAM,
        )
    )
    check_for_error(create_session_response.status)

    session = create_session_response.session
    print("Session Created Successfully.\n")

    print("Writing 10 frames to CAN Interface.\n")

    #Set CAN Header Data Rate
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_BAUD_RATE_64,
            u64_scalar=1000000,
        )
    )
    check_for_error(set_property_response.status)

    #Set Message FD Data Rate
    set_property_response = client.SetProperty(
        nixnet_types.SetPropertyRequest(
            session=session,
            property_id=nixnet_types.PROPERTY_SESSION_INTF_CAN_FD_BAUD_RATE_64,
            u64_scalar=1000000,
        )
    )
    check_for_error(set_property_response.status)



    while i < 10:
        

        # Update the frame data
        write_frame_response = client.WriteFrame(
            nixnet_types.WriteFrameRequest(session=session, buffer=canfdframes, timeout_raw= 10.0)
        )
        check_for_error(write_frame_response.status)

        print("Frame sent:")
      
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
    if session:
        # clear the XNET session.
        check_for_error(client.Clear(nixnet_types.ClearRequest(session=session)).status)
        print("Session cleared successfully!\n")
