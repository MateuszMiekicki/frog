import json
import zmq
import threading
import sched
import time
import psycopg2
import logging
import datetime

PULLER_HOST = 'toad'
PULLER_PORT = 5572

DATABASE = 'smart-terrarium'
DATABASE_HOST = 'postgresql'
USER = 'frog'
PASSWORD = 'frog!123'
PORT = 5432

logging.basicConfig(level=logging.DEBUG)


def connect_to_database():
    conn = psycopg2.connect(database=DATABASE,
                            host=DATABASE_HOST,
                            user=USER,
                            password=PASSWORD,
                            port=PORT)
    return conn


class DeviceRepository():
    def __init__(self, conn):
        self.conn = conn

    def get_mac_address_by_mac_address(self, mac_address):
        cur = self.conn.cursor()
        device_id = None
        try:
            cur.execute(
                f"SELECT id FROM device WHERE mac_address='{mac_address}';")
            device_id = cur.fetchone()
        except Exception as e:
            logging.warning(e)
        cur.close()
        logging.debug(f"device_id: {device_id}, mac_address: {mac_address}")
        return device_id


class SensorRepository():
    def __init__(self, conn):
        self.conn = conn

    def get_sensor_by_device_id_and_pin_number(self, device_id, pin_number):
        cur = self.conn.cursor()
        sensor_id = None
        try:
            cur.execute(
                f"SELECT id FROM sensor WHERE device_id={device_id} AND pin_number={pin_number};")
            sensor_id = cur.fetchone()
        except Exception as e:
            logging.warning(e)
        cur.close()
        return sensor_id


class Alert():
    def __init__(self, mac_address, pin_number, alert_number, date, description, priority, served):
        self.mac_address = mac_address
        self.pin_number = pin_number
        self.alert_number = alert_number
        self.date = date
        self.description = description
        self.priority = priority
        self.served = served
        self.__fill_mandatory_fields_defaults_if_not_present()

    def __fill_mandatory_fields_defaults_if_not_present(self):
        if self.date is None:
            self.date = datetime.datetime.now()
        if self.pin_number is None:
            self.pin_number = 'null'

    def is_valid_alert(self):
        if self.mac_address is None or self.alert_number is None or self.description is None or self.priority is None or self.served is None:
            return False
        return True

    def __str__(self):
        return f'Alert: mac_address: {self.mac_address}, pin_number: {self.pin_number}, alert_number: {self.alert_number}, date: {self.date}, description: {self.description}, priority: {self.priority}, served: {self.served}'


class Device():
    def __init__(self, device_id):
        self.device_id = device_id
        self.sensor_ids = {}

    def add_sensor_id(self, sensor_id, pin_number):
        self.sensor_ids[pin_number] = sensor_id

    def get_sensor_id(self, pin_number):
        return self.sensor_ids.get(pin_number)


class DeviceMatcher():
    def __init__(self, device_repository: DeviceRepository, sensor_repository: SensorRepository):
        self.device_repository = device_repository
        self.sensor_repository = sensor_repository
        self.cache = {}

    def get_device_id(self, mac_address):
        device_id = self.cache.get(mac_address)
        if device_id is None:
            device_id = self.device_repository.get_mac_address_by_mac_address(
                mac_address)
            if device_id is None:
                logging.warning(
                    f"device with mac_address {mac_address} not found")
                return None
            device_id = device_id[0]
            self.cache[mac_address] = device_id
        return device_id

    def get_sensor_id(self, device_id, pin_number):
        device = self.cache.get(device_id)
        if device is None:
            device = Device(device_id)
            self.cache[device_id] = device
        sensor_id = device.get_sensor_id(pin_number)
        if sensor_id is None:
            sensor_id = self.sensor_repository.get_sensor_by_device_id_and_pin_number(
                device_id, pin_number)
            if sensor_id is None:
                return None
            sensor_id = sensor_id[0]
            device.add_sensor_id(sensor_id, pin_number)
        return sensor_id


class AlertRepository():
    def __init__(self, conn, device_matcher: DeviceMatcher):
        self.conn = conn
        self.device_matcher = device_matcher

    def __get_sensor_id(self, device_id, pin_number):
        sensor_id = 'null'
        if pin_number != 'null':
            sensor_id = self.device_matcher.get_sensor_id(
                device_id, pin_number)
        return sensor_id

    def __prepare_insert_query(self, device_id, sensor_id, alert):
        return f"INSERT INTO alert (device_id, sensor_id, alert_number, date, description, priority, served) VALUES ({device_id}, {sensor_id}, {alert.alert_number}, '{alert.date}', '{alert.description}', {alert.priority}, {alert.served});"

    def __prepare_alert_when_insert_fails_query(self, device_id, alert, e):
        return f"INSERT INTO alert (device_id, sensor_id, alert_number, date, description, priority, served) VALUES ({device_id}, 'null', {alert.alert_number}, '{alert.date}', 'error during insert: {e}', 10000, {alert.served});"

    def __insert(self, cur, device_id, sensor_id, alert):
        try:
            cur.execute(self.__prepare_insert_query(
                device_id, sensor_id, alert))
            self.conn.commit()
        except Exception as e:
            logging.warning(e)
            self.conn.rollback()
            cur.execute(
                self.__prepare_alert_when_insert_fails_query(device_id, alert, e))
            self.conn.commit()

    def insert_alerts(self, alerts):
        cur = self.conn.cursor()
        for alert in alerts:
            if not alert.is_valid_alert():
                logging.warning(
                    f"alert is not valid, skipping alert insert: {alert}")
                continue

            device_id = self.device_matcher.get_device_id(alert.mac_address)
            if device_id is None:
                logging.warning("device_id is None, skipping alert insert")
                continue

            sensor_id = self.__get_sensor_id(device_id, alert.pin_number)

            self.__insert(cur, device_id, sensor_id, alert)
        cur.close()


def serialize(message) -> Alert:
    message = json.loads(message)
    if message.get('alert') is None:
        logging.warning(f"message does not contain alert: {message}")
        return None

    message = message.get('alert')
    mac_address = message.get('mac_address')
    pin_number = message.get('pin_number')
    if pin_number is None:
        logging.debug("pin_number is None, setting to 'null'")
        pin_number = 'null'
    alert_number = message.get('alert_number')
    date = message.get('date')
    description = message.get('description')
    priority = message.get('priority')
    served = message.get('served')
    if served is None:
        served = False
    return Alert(mac_address, pin_number, alert_number, date, description, priority, served)


class AlertBuffer():
    def __init__(self, scheduler: sched.scheduler, alert_repository: AlertRepository):
        self.scheduler = scheduler
        self.alert_repository = alert_repository
        self.alerts = []

    def __push_alerts_to_database(self):
        self.alert_repository.insert_alerts(self.alerts)
        self.clear_alerts()
        self.scheduler.enter(5, 1, self.__push_alerts_to_database)

    def add_alert(self, alert):
        self.alerts.append(alert)

    def get_alerts(self):
        return self.alerts

    def clear_alerts(self):
        self.alerts = []

    def run(self):
        self.scheduler.enter(5, 1, self.__push_alerts_to_database)
        self.scheduler.run()


class Notifier():
    def __init__(self, port: int):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

    def notify(self, topic, message):
        self.socket.send(f'{topic} {message}'.encode('utf-8'))


class Puller():
    def __init__(self, alert_buffer: AlertBuffer, host: str, port: int):
        self.alert_buffer = alert_buffer
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PULL)
        self.socket.connect(f"tcp://{host}:{port}")
        self.notifier = Notifier(5574)

    def pull(self):
        message = self.socket.recv()
        alert = serialize(message)
        logging.debug(f"alert: {alert}")
        if alert is None:
            return None
        self.notifier.notify(alert.mac_address, message)
        return alert

    def pull_and_add_to_buffer(self):
        alert = self.pull()
        if alert is not None:
            self.alert_buffer.add_alert(alert)

    def run(self):
        thread = threading.Thread(target=self.alert_buffer.run)
        thread.start()
        while True:
            self.pull_and_add_to_buffer()


def main():
    scheduler = sched.scheduler(time.time, time.sleep)

    db_connection = connect_to_database()
    logging.info("connected to database")
    device_repository = DeviceRepository(db_connection)
    sensor_repository = SensorRepository(db_connection)
    device_matcher = DeviceMatcher(device_repository, sensor_repository)
    alert_repository = AlertRepository(db_connection, device_matcher)

    alert_buffer = AlertBuffer(scheduler, alert_repository)
    puller = Puller(alert_buffer, PULLER_HOST, PULLER_PORT)
    thread = threading.Thread(target=puller.run)
    thread.start()
    logging.info("started notifier")


if __name__ == '__main__':
    main()
