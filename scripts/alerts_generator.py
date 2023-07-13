#create zmq pull push server with push message for device with correct mac address

import zmq


def main():
    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://*:9999")
    