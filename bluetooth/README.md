# ESP32 蓝牙模块

---

[toc]

---

使用 ESP32 开发板的蓝牙模块，与其他有蓝牙功能的设备建立通信。

## 步骤

### 安装依赖

使用低功耗蓝牙（BLE），核心是官方的 `bluetooth` 模块。不过，更推荐使用基于 `asyncio` 的高级封装库 `aioble`，它能用更简洁的代码实现复杂的蓝牙功能。

1. **安装 `mpremote`**：在电脑（而非 ESP32-S3）上，确保已安装 `mpremote`。

    ```bash
    pip install mpremote
    ```

2. **连接设备**：通过 USB 线将 ESP32-S3 连接到电脑。

3. **执行安装命令**：在电脑的终端（命令行）中运行以下命令。

    ```bash
    mpremote mip install aioble
    ```

    这个命令会直接将 `aioble` 包安装到你的 ESP32-S3 设备的 `/lib` 目录下。

    > [!TIP]
    >
    > 如果出现 `mpremote: no device found` 错误，请检查 ESP32-S3 是否成功连接，以及端口是否被其他应用（如 Thonny）占用。

### 开启蓝牙广播

使用 Thonny，将 [`esp32.py`](esp32.py) 另存为 ESP32 开发板上的 `main.py` 文件，运行。

### 建立连接

在电脑上安装依赖库：

```bash
pip install bleak
```

运行 [`pc.py`](pc.py) 。

> [!TIP]
>
> 如果扫描到的 UUID 是以前写过的旧服务的，而不是当前正在运行的，可以考虑删除蓝牙缓存：打开「设置 → 蓝牙和其他设备」→ 找到旧设备 → 删除 → 关闭再打开蓝牙。

## 输出

预期标准输出：

- ESP32：

    ```
    已注册服务 UUID: UUID('7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f60')
    接收特征 UUID: UUID('7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f61')
    发送特征 UUID: UUID('7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f62')
    已连接: Device(ADDR_PUBLIC, dc:45:46:c0:20:1e, CONNECTED)
    收到: b'Hello from PC!'
    已断开
    ```

- 电脑端：

    ```
    已连接: True
    服务: 00001800-0000-1000-8000-00805f9b34fb
      特征: 00002a00-0000-1000-8000-00805f9b34fb 属性: ['read']
      特征: 00002a01-0000-1000-8000-00805f9b34fb 属性: ['read']
    服务: 00001801-0000-1000-8000-00805f9b34fb
      特征: 00002a05-0000-1000-8000-00805f9b34fb 属性: ['indicate']
      特征: 00002b3a-0000-1000-8000-00805f9b34fb 属性: ['read']
      特征: 00002b29-0000-1000-8000-00805f9b34fb 属性: ['write', 'read']
    服务: 7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f60
      特征: 7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f61 属性: ['write']
      特征: 7e2f1a10-4b3c-4d5e-8f9a-1b2c3d4e5f62 属性: ['notify', 'read']
    已订阅通知，等待数据...
    收到通知: bytearray(b'Echo:Hello from PC!')
    已发送数据
    ```

