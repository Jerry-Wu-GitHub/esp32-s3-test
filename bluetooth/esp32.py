# The main.py file on ESP32.

import aioble
import bluetooth
import asyncio


_DEVICE_NAME = "ESP32-BiDi"
_SERVICE_UUID = bluetooth.UUID("7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f60")
_RX_CHAR_UUID = bluetooth.UUID("7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f61")  # PC 写入
_TX_CHAR_UUID = bluetooth.UUID("7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f62")  # PC 订阅

service = aioble.Service(_SERVICE_UUID)
rx_char = aioble.Characteristic(service, _RX_CHAR_UUID, write=True, capture=True)
tx_char = aioble.Characteristic(service, _TX_CHAR_UUID, read=True, notify=True)
aioble.register_services(service)

print("已注册服务 UUID:", _SERVICE_UUID)
print("接收特征 UUID:", _RX_CHAR_UUID)
print("发送特征 UUID:", _TX_CHAR_UUID)


async def receive_task():
    """
    收到 PC 端发来的消息。
    """
    while True:
        connection, data = await rx_char.written()
        print("收到:", data)
        tx_char.write(b"Echo:" + data, send_update=True)


async def peripheral_task():
    """
    持续广播蓝牙。断掉后继续广播。
    """
    while True:
        async with await aioble.advertise(
            250_000, name=_DEVICE_NAME, services=[_SERVICE_UUID]
        ) as connection:
            print("已连接:", connection.device)
            await connection.disconnected()
            print("已断开")


async def main():
    await asyncio.gather(peripheral_task(), receive_task())


if __name__ == '__main__':
    asyncio.run(main())
