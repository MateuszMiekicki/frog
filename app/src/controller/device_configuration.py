from fastapi import APIRouter, status, Request, HTTPException
from controller.dto.user import User
import controller.facade.user_repository as facade_repository
import controller.facade.user_authenticator as facade_authenticator
import zmq
import time
router = APIRouter()

zmq_server_address = 'tcp://localhost:5555'


@router.get('/device/{device_id}/configuration', status_code=status.HTTP_200_OK)
async def get_config(request: Request):
    # context = zmq.Context()
    # socket = context.socket(zmq.REQ)
    # socket.connect(zmq_server_address)
    # socket.send_string("Hello, server!")
    # response = ''
    # if socket.poll(timeout=1000):
    #     response = socket.recv_string()
    #     print("Response:", response)
    # else:
    #     print("Przekroczono limit czasu oczekiwania")
    # socket.close()
    # context.term()
    return '''
    "MQTT":{
      "MQTT_ID_NAME": "ESP32",
      "MQTT_PORT": "1883",
      "MQTT_SERVER_IP": "192.168.26.186",
      "MQTT_CONNECTION_TEMPLATE" : {"device_id": 1, "sensor_id": "", "value": ""}
      },

      "TCP":{
      "TCP_SERVER_IP": "192.168.26.186",
      "TCP_PORT": "6666"
      },

    "BUTTONS":{
      "BUTTON_ADC_PIN": "6"
      },

    "PWM":{
       "PWM_PIN": "10"
    },

    "WIFI":{
      "WIFI_SSID": "Redmi",
      "WIFI_PASSWORD": "12345678",
      "ESP_MAC_ADDRESS": "7c:df:a1:3f:2e:ac"
      },

    "LCD":{
      "LCD_WIDTH" : "320",
      "LCD_HEIGHT" : "240",
      "LCD_ROTATION": "0",



      "LCD_CLK_PIN" : "15",
      "LCD_MOSI_PIN" : "9",
      "LCD_MISO_PIN" : "8",



      "LCD_CS_PIN" : "11",
      "LCD_RST_PIN" : "16",
      "LCD_DC_PIN" : "13",



      "FONT_DIR" : "fonts/Unispace12x24.c",
      "FONT_WIDTH" : "12",
      "FONT_HEIGHT" : "24"
      },

    "SENSORS":[
        {
            "pin_number" : 501,
            "category" : "humidity",
            "min_val" : 50,
            "max_val" : 80
            },
        {
            "pin_number" : 502,
            "category" : "temperature",
            "min_val" : 20,
            "max_val" : 30
            }
    ]
}'''
