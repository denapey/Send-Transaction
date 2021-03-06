import socket
import sys

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = './vault_socket'
print('connecting to {}'.format(server_address))
try:
    sock.connect(server_address)
except socket.error as msg:
    print(msg)
    sys.exit(1)

try:
    # Send data
    # message = b"""{"id": "1", "type": "sign_transfer", "from_address": "0x69dB21E25AF4eE4d23bF340011F5a88Bf4D80033", "to_address": "0xc00DE490c026A1946E1fAeeaF4bB1F46d55A0308", "amount": "1"}
# {"id": "2", "type": "sign_transfer", "from_address": "0x69dB21E25AF4eE4d23bF340011F5a88Bf4D80033", "to_address": "0xc00DE490c026A1946E1fAeeaF4bB1F46d55A0308", "amount": "1"}"""

    message = b"""{"id": "1", "type": "sign_transfer", "from_address": "0x69dB21E25AF4eE4d23bF340011F5a88Bf4D80033", "to_address": "0xc00DE490c026A1946E1fAeeaF4bB1F46d55A0308", "amount": "0.1"}"""

    print('sending {!r}'.format(message))
    sock.sendall(message)

    full_msg = ''

    while True:
        # Receive the data in small chunks and combine it
        msg = sock.recv(16)     
        full_msg = full_msg + msg.decode("utf-8")
        if len(msg) < 16:
            break

    # print(full_msg)

    print('received :', full_msg)

finally:
    print('closing socket')
    sock.close()
