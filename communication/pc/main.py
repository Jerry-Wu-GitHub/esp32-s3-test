# Script running on PC.

import asyncio
import json
from bleak import BleakClient, BleakScanner


DEVICE_NAME = "ESP32-BiDi"
RX_CHAR_UUID = "7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f61"  # 对应 ESP32 的 rx_char
TX_CHAR_UUID = "7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f62"  # 对应 ESP32 的 tx_char

CHUNK_SIZE = 20  # 默认 MTU 23 - 3 字节 ATT 头 = 20

_buffer = bytearray()

async def notification_handler(sender, data_bytes):
    """
    收到 ESP32 发来的数据后的行为。
    """
    global _buffer
    _buffer.extend(data_bytes)
    while b"\n" in _buffer:
        line, _, rest = _buffer.partition(b"\n")
        _buffer = bytearray(rest)
        try:
            print(line.decode("utf-8"))
        except UnicodeError:
            print(line)



async def ainput(prompt: str = "") -> str:
    """在线程中执行 input，避免阻塞 asyncio 事件循环。"""
    return await asyncio.to_thread(input, prompt)


async def send_chunks(client: BleakClient, data: bytes,
                      chunk_size: int = CHUNK_SIZE):
    """BLE 单次写入 payload 受 MTU 限制，这里手动分片。"""
    total = len(data)
    n = (total + chunk_size - 1) // chunk_size
    print(f"发送 {total} 字节，分 {n} 片")
    for i in range(0, total, chunk_size):
        chunk = data[i:i + chunk_size]
        await client.write_gatt_char(RX_CHAR_UUID, chunk, response=True)


async def connect_wlan(client: BleakClient) -> bool | None:
    """
    Returns:
        - True: 成功向 ESP32 发送 WLAN 信息。
        - False: 没有成功向 ESP32 发送 WLAN 信息。
        - None: 用户没有输入 SSID。
    """
    await ainput("[按下回车以输入]")
    ssid = await ainput("请输入要连接的 WLAN SSID：")
    if not ssid:
        return None

    password = await ainput("请输入网络密码：")

    # 发送数据到 ESP32
    wlan_data = {"ssid": ssid, "password": password}
    payload = json.dumps(wlan_data, ensure_ascii=False).encode("utf-8")
    await send_chunks(client, payload)
    return True



async def main():
    # 寻找蓝牙设备
    device = await BleakScanner.find_device_by_name(DEVICE_NAME)
    if not device:
        print("未找到设备")
        return

    # 建立连接
    async with BleakClient(device) as client:
        print("已连接:", client.is_connected)
        for service in client.services:
            print("服务:", service.uuid)
            for char in service.characteristics:
                print("  特征:", char.uuid, "属性:", char.properties)

        # 订阅通知以接收数据
        await client.start_notify(TX_CHAR_UUID, notification_handler)
        print("已订阅通知，等待数据...")

        # 监听用户输入
        keep_going = True
        while keep_going:
            result = await connect_wlan(client)
            keep_going = result is not None

        await client.stop_notify(TX_CHAR_UUID)


if __name__ == '__main__':
    asyncio.run(main())
