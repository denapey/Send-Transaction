import socket
import sys
import os
import json
from web3 import Web3

# Connect to infura.io
infura_url = "https://ropsten.infura.io/v3/<Project_id>";
w3 = Web3(Web3.HTTPProvider(infura_url))
print('Check Connection : ', w3.isConnected())
# print(w3.eth.blockNumber)

# Creates and listens on an Unix domain socket 
server_address = './vault_socket'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except OSError:
    if os.path.exists(server_address):
        raise

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the address
print('starting up on {}'.format(server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # (issue no.1) get whole messages and put them into a variabel before the next process
        full_data = ''
        while True:
            # Receive the data in small chunks and combine it
            data = connection.recv(16)     
            full_data = full_data + data.decode("utf-8")
            if len(data) < 16:
                break

        # print('full data :', full_data)

        if full_data != "":
            #print('process full_data : ', full_data)

            res = "" 
            # split full_data by new line
            string_count = len(full_data.splitlines())

            for new_data in full_data.splitlines():

                # convert json string data to dict
                data_dict = json.loads(new_data)

                account_1 = data_dict['from_address']
                account_2 = data_dict['to_address']

                # read private key from file, the private key for from_address is stored in a file (.key)
                keyfile = '{}.key'.format(account_1)

                f = open(keyfile, "r")
                pkey = f.readline()
                f.close()

                # calculete fee transaktion before send the transaction
                gas_price = w3.eth.gas_price
                amount = w3.toWei(data_dict['amount'],'ether')
                estimateGas = w3.eth.estimateGas({'to': account_2, 'from': account_1, 'value': amount})
                transaction_cost = gas_price * estimateGas

                # calculate fee transaktion to be included in amount
                total_amount = amount - transaction_cost

                # print('Estimate Fee transaction:', w3.fromWei(transaction_cost, 'ether'))
                # print('Total amount:', w3.fromWei(total_amount, 'ether'))

                # construct and sign a transaction
                signed_txn = w3.eth.account.signTransaction(dict(
                    nonce= w3.eth.getTransactionCount(account_1),
                    gasPrice = w3.eth.gasPrice, 
                    gas=30000,
                    to=account_2,
                    value=total_amount
                    ),
                pkey)

                # Get sign transaction
                # print('sign Transaction : ', w3.toHex(signed_txn.hash))
                signTransaction = w3.toHex(signed_txn.hash)

                # (issue no.2) don't send transaction 
                # trx = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
                # w3.toHex(trx)

                # create response variabel
                # (issue no.3) change trx to tx -> typo
                data_trx = {
                    'id': data_dict['id'],
                    'tx': signTransaction,
                    }                          
                res = res + json.dumps(data_trx)

                # if data from client more than 1 row, add new line to each data response
                if (string_count > 1):
                    res = res + '\n'

            # send respon to client with data type bytes
            print('sending data back to the client')
            connection.sendall(res.encode('utf-8'))

        else:
            print('no data from', client_address)


    finally:
        # Clean up the connection
        connection.close()
