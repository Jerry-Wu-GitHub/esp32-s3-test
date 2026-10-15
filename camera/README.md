# 摄像头

---

[toc]

---

本实验使用的开发板型号是 ESP32-S3-CAM。

摄像头型号是 GC2145。

## 烧录固件

### 下载固件

在 [micropython-camera-API](https://github.com/cnadler86/micropython-camera-API/releases) 下载名字里带“ESP32_GENERIC-SPIRAM”的压缩包，解压，得到 `.bin` 固件文件。

### 烧录固件

1. 安装 esptool：

    ```bash
    pip install esptool
    ```

2. 进入下载模式：按住 **BOOT** 不放 → 短按 RESET → 松开 RESET，**继续按住 BOOT**。保持这个状态。

3. 先全盘擦除 Flash：（请替换 `<PORT>` 为你的实际串口，如 `COM3` 或 `/dev/ttyUSB0`）

    ```bash
    esptool --chip esp32s3 --port <PORT> erase_flash
    ```

4. 烧录固件：

    ```bash
    esptool --chip esp32s3 --port <PORT> write_flash 0x0 path/to/firmware.bin
    ```

5. 完成：烧录跑完，松开 BOOT，按 RESET 复位板子。

## 测试摄像头

用 Thonny 与开发板连接，在 Thonny Shell 输入

```python
import camera
```

应该会导入成功。

导入成功后，将 [`esp32.py`](esp32.py) 另存为开发板上的 `main.py` 文件，运行。不出意外的话，刷新 Thonny 左下角的“MicroPython设备”就能看到图片文件了。可以把图片文件下载到自己的电脑上查看。
