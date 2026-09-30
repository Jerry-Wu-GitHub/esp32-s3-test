# ESP32 通信实验

综合了蓝牙和 WiFi 功能，先连接蓝牙来传递 WiFi 名和密码，再连接 WiFi。

## 步骤

### 安装依赖

参见[安装 `aioble`](../bluetooth/README.md#安装依赖)。

### 启动开发板

把 [`esp32`](./esp32) 文件夹下的文件烧录到开发板，运行。

### 启动客户端

在电脑上[安装 `bleak` 库](../bluetooth/README.md#建立连接)，运行 [`pc/main.py`](pc/main.py) 。
