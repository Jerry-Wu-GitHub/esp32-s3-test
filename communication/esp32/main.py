# The main.py file on ESP32.

import aioble
import asyncio
import bluetooth
import network
import time
import ujson
import urequests

# 蓝牙
_DEVICE_NAME = "ESP32-BiDi"
_SERVICE_UUID = bluetooth.UUID("7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f60")
_RX_CHAR_UUID = bluetooth.UUID("7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f61")  # PC 写入
_TX_CHAR_UUID = bluetooth.UUID("7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f62")  # PC 订阅

_BLE_CHUNK = 20  # 保守值，对应默认 MTU 23 的 payload

_send_lock = asyncio.Lock()

async def ble_send(tx_char, data: bytes, chunk: int = _BLE_CHUNK):
    """把长消息切成 ≤chunk 字节的分片逐条 notify。同一时刻只有一条消息在发。"""
    payload = data + b"\n"
    async with _send_lock:
        for i in range(0, len(payload), chunk):
            tx_char.write(payload[i:i + chunk], send_update=True)
            await asyncio.sleep_ms(5)   # 给 BLE 栈一点时间，避免通知队列溢出


async def scan_wlan(wlan, tx_char):
    networks = wlan.scan()
    print(f"扫描到 {len(networks)} 个网络:")
    await ble_send(tx_char, f"扫描到 {len(networks)} 个网络:".encode("utf-8"))
    for net in networks:
        ssid = net[0].decode('utf-8', 'ignore')
        channel = net[2]
        rssi = net[3]
        line = f"  SSID: {ssid:<30} 信道: {channel:<4} 信号: {rssi}dBm"
        print(line)
        await ble_send(tx_char, line.encode("utf-8"))


def get_ip():
    response = urequests.get('http://httpbin.org/ip')
    print('状态码:', response.status_code)
    print('响应内容:', response.text)
    response.close()


async def receive(rx_char, tx_char, wlan):
    buffer = b""
    while True:
        connection, bytes_data = await rx_char.written()
        print("收到片段:", bytes_data)
        buffer += bytes_data

        if len(buffer) > 4096:
            print("缓冲区溢出，重置。")
            await ble_send(tx_char, b"Error: buffer overflow")
            buffer = b""
            continue

        try:
            json_str = buffer.decode("utf-8")
            json_data = ujson.loads(json_str)
        except (UnicodeError, ValueError):
            continue

        buffer = b""
        print("解析成功:", json_str)
        await ble_send(tx_char, b"Receive:" + json_str.encode("utf-8"))

        if "ssid" not in json_data:
            await ble_send(tx_char, b"Error: Missing `ssid` field.")
            continue
        ssid = json_data["ssid"]

        if "password" not in json_data:
            await ble_send(tx_char, b"Error: Missing `password` field.")
            continue
        password = json_data["password"]

        if wlan.isconnected():
            print("正在断开当前网络...")
            wlan.disconnect()
            while wlan.isconnected():
                time.sleep_ms(100)
            print("已断开连接。")

        print(f"正在连接到 {ssid} ...")
        wlan.connect(ssid, password)

        timeout = 30
        while not wlan.isconnected() and timeout > 0:
            print(f'状态码: {wlan.status()}', end=' ')
            time.sleep(1)
            timeout -= 1

        if wlan.isconnected():
            print('\n连接成功！')
            await ble_send(tx_char, b"Successfully connected!")
            try:
                get_ip()
            except Exception as e:
                print('请求失败:', e)
        else:
            print(f'\n连接失败，最终状态码: {wlan.status()}')
            await ble_send(
                tx_char,
                f"Connection failed. Status code: {wlan.status()}".encode("utf-8")
            )



async def peripheral(
    service_uuid: str,
    rx_char: aioble.Characteristic,
    tx_char: aioble.Characteristic,
    wlan: network.WLAN,
):
    """
    持续广播蓝牙。断掉后继续广播。
    """
    while True:
        async with await aioble.advertise(
            250_000, name=_DEVICE_NAME, services=[_SERVICE_UUID]
        ) as connection:
            print("蓝牙已连接:", connection.device)

            # 扫描可用的网络
            await scan_wlan(wlan, tx_char)

            # 等待蓝牙断开
            await connection.disconnected()
            print("蓝牙已断开")


async def main():
    # 无线网
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    time.sleep(1)

    # 蓝牙
    service = aioble.Service(_SERVICE_UUID)
    rx_char = aioble.Characteristic(service, _RX_CHAR_UUID, write=True, capture=True)
    tx_char = aioble.Characteristic(service, _TX_CHAR_UUID, read=True, notify=True)
    aioble.register_services(service)

    print("已注册服务 UUID:", _SERVICE_UUID)
    print("接收特征 UUID:", _RX_CHAR_UUID)
    print("发送特征 UUID:", _TX_CHAR_UUID)

    peripheral_task = peripheral(_SERVICE_UUID, rx_char, tx_char, wlan)
    receive_task = receive(rx_char, tx_char, wlan)
    await asyncio.gather(peripheral_task, receive_task)


if __name__ == '__main__':
    asyncio.run(main())
