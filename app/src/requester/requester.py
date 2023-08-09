from configuration import configuration
from enum import Enum
import zmq
import zmq.asyncio
import logging
import json


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"


class MessagePurpose(Enum):
    SET_CONFIGURATIONS = "set_configuration"
    GET_CONFIGURATIONS = "get_configuration"
    SET_SENSOR_CONFIGURATION = "set_sensor_configuration"


class Message():
    def __init__(self, type: MessageType, purpose: MessagePurpose, payload: str):
        self.type = type
        self.purpose = purpose
        self.payload = payload

    def __str__(self):
        return f'{self.type.value} {self.purpose.value} {self.payload}'

    def is_valid_message(self):
        if self.type in MessageType and self.purpose in MessagePurpose:
            if self.purpose is MessagePurpose.SET_CONFIGURATIONS:
                return self.payload is not None
            return True
        return False


def build_request_get_configurations():
    return Message(MessageType.REQUEST, MessagePurpose.GET_CONFIGURATIONS, {})


def build_request_set_configurations(payload):
    payload = {
        "configuration": payload
    }
    return Message(MessageType.REQUEST, MessagePurpose.SET_CONFIGURATIONS, payload)


def build_request_set_sensor_configuration(payload: list[dict]):
    payload = {
        "sensors": payload
    }
    return Message(MessageType.REQUEST, MessagePurpose.SET_SENSOR_CONFIGURATION, payload)


def serialize(message: Message):
    output = {
        "type": message.type.value,
        "purpose": message.purpose.value,
        "payload": message.payload
    }
    output = str(output).replace("'", '"')
    logging.debug(f"Serialized message: {output}")
    return output


class RequestStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class Requester():
    def __init__(self, zmq_config: configuration.ConfigForRequest):
        import sys
        if 'win32' in sys.platform:
            import asyncio
        self.zmq_config = zmq_config

    async def __send_request(self, client_id: str, request: str, close_socket: bool = True):
        logging.debug(
            f"Sending request to {self.zmq_config.get_receiver_address()} by {client_id}")
        client = self.zmq_config.zmq_context.socket(zmq.DEALER)
        client.identity = client_id.encode()
        client.connect(self.zmq_config.get_receiver_address())
        client.send(request.encode())
        logging.debug(f"'{client_id}' send request: {request}")
        if close_socket:
            logging.debug(
                f"close socket for '{client_id}' after sending request")
            client.close()
            return None
        return client

    async def __receive_response(self, socket: zmq.Socket):
        async_poller = zmq.asyncio.Poller()
        async_poller.register(socket, zmq.POLLIN)
        logging.debug(
            f"Waiting for response from server by {self.zmq_config.get_timeout()}")
        if await async_poller.poll(self.zmq_config.get_timeout()*1000):
            response = await socket.recv()
            logging.debug(f"{socket.identity} received response: {response}")
            return response
        logging.debug(f"{socket.identity} no response from server - timeout")
        return None

    async def __send_request_and_receive_response(self, client_id: str, request: str):
        dont_close_socket = False
        client = await self.__send_request(client_id, request, dont_close_socket)
        response = await self.__receive_response(client)
        client.close()
        return response

    async def send_request(self, client_id: str, message: Message):
        if not message.is_valid_message():
            raise Exception('Invalid message')
        await self.__send_request(client_id, serialize(message))

    async def send_request_and_receive_response(self, client_id: str, message: Message):
        if not message.is_valid_message():
            raise Exception('Invalid message')
        response = await self.__send_request_and_receive_response(
            client_id, serialize(message))
        return response


class DeviceRequester():
    def __init__(self, requester: Requester):
        self.requester = requester

    # def send_set_configuration_request_to_device(self, mac_address: str, configuration: str):
    #     message = MessageBuilder(
    #         configuration).build_request_set_configurations()
    #     requester.send(mac_address, message)

    async def send_get_configuration_request_to_device(self, mac_address: str):
        message = build_request_get_configurations()
        return await self.requester.send_request_and_receive_response(mac_address, message)

    async def send_set_configuration_request_to_device(self, mac_address: str, configuration):
        message = build_request_set_configurations(configuration)
        return await self.requester.send_request_and_receive_response(mac_address, message)

    async def send_set_sensor_configuration_request_to_device(self, mac_address: str,  sensors: list[dict]):

        configuration = [{"pin_number": int(sensor.pin_number), "type": sensor.type,
                          "min_value": float(sensor.min_value), "max_value": float(sensor.max_value)} for sensor in sensors]
        message = build_request_set_sensor_configuration(configuration)
        return await self.requester.send_request_and_receive_response(mac_address, message)
