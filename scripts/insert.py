from questdb.ingress import Sender, IngressError, TimestampMicros, TimestampNanos
import sys
import datetime
import random
import time


def example(host: str = 'questdb', port: int = 9009):
    try:
        with Sender(host, port) as sender:
            for i in range(1, 1000):
                time.sleep(random.uniform(0.1, 0.8))
                timestamp = TimestampNanos.now()

                sender.row(
                    'sensor_data',
                    columns={
                        'device_id': 2 if i % 2 == 0 else 1,
                        'sensor_id': random.randint(1, 8),
                        'value': 28.0 - random.uniform(-8, 10)
                    }, at=timestamp
                )
                sender.flush()

    except IngressError as e:
        sys.stderr.write(f'Got error: {e}\n')


if __name__ == '__main__':
    example()
