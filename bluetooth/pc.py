# Script running on PC.

import asyncio
from bleak import BleakClient, BleakScanner


DEVICE_NAME = "ESP32-BiDi"
RX_CHAR_UUID = "7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f61"  # 对应 ESP32 的 rx_char
TX_CHAR_UUID = "7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f62"  # 对应 ESP32 的 tx_char


async def notification_handler(sender, data):
    """
    收到 ESP32 发来的数据后的行为。
    """
    print(f"收到通知: {data}")


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

        # 向ESP32发送数据
        await client.write_gatt_char(RX_CHAR_UUID, b"Hello from PC!")
        print("已发送数据")

        await asyncio.sleep(5)  # 保持连接一段时间
        await client.stop_notify(TX_CHAR_UUID)


if __name__ == '__main__':
    asyncio.run(main())
