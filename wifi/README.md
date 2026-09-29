# ESP32 WiFi 模块

---

[toc]

---

使用 ESP32 开发板的 WiFi 模块，使其具备访问局域网甚至公网的能力。

本实验连接的 WiFi 只需要获得名称（SSID）和密码就能连接，而不需要 WPA2-Enterprise 之类的认证。

## 步骤

### 确保 WiFi 存在

为了能获得可用的网络环境，推荐连接手机移动热点或者一般的家用路由器，而不是需要“用户名+密码”认证的校园网。

> [!CAUTION]
>
> ESP32-S3 仅支持 **2.4GHz** 频段的 WiFi。
>
> 因此，使用手机热点时，注意要在热点设置里将 AP 频段选择为 2.4GHz。

确保处于 WiFi 覆盖范围后，向开发板烧录并运行以下代码：

```python
import network
import time

wlan = network.WLAN(network.STA_IF)

# 可选：执行一次“关闭-重开”的循环，让 scan() 正常工作
# wlan.active(False)
# time.sleep(0.5)
# wlan.active(True)
# time.sleep(1)

networks = wlan.scan()
print(f"扫描到 {len(networks)} 个网络:")
for net in networks:
    ssid = net[0].decode('utf-8', 'ignore')
    channel = net[2]
    rssi = net[3]
    print(f"  SSID: {ssid:<30} 信道: {channel:<4} 信号: {rssi}dBm")
```

这会输出扫描到的无线网络名和信号强度，例如：

```
扫描到 7 个网络:
  SSID: 401                            信道: 6    信号: -60dBm
  SSID: 9501                           信道: 6    信号: -74dBm
  SSID: 哈基米南北绿豆          信道: 5    信号: -83dBm
  SSID:                                信道: 6    信号: -84dBm
  SSID: TP-LINK_799C                   信道: 1    信号: -92dBm
  SSID: Redmi_72C7                     信道: 4    信号: -92dBm
  SSID:                                信道: 8    信号: -92dBm
```

检查输出列表里有没有你要连接的网络名，如果没有的话，请检查网络存在性和频段是否符合要求。

### 连接网络

只需要知道待连接网络的 SSID 和密码即可。

向开发板烧录并运行以下代码：

```python
import network
import time

SSID = '网络名称'
PASSWORD = '密码'

wlan = network.WLAN(network.STA_IF)
wlan.active(False)
time.sleep(0.5)
wlan.active(True)
time.sleep(1)

# 可选：如果连接不稳定，降低发射功率试试
# wlan.config(txpower=15)

print('正在连接 WiFi...')
wlan.connect(SSID, PASSWORD)

timeout = 30
while not wlan.isconnected() and timeout > 0:
    print(f'状态码: {wlan.status()}', end=' ')
    time.sleep(1)
    timeout -= 1

if wlan.isconnected():
    print('\n连接成功！')
    print('IP 地址等信息:', wlan.ifconfig())
else:
    print(f'\n连接失败，最终状态码: {wlan.status()}')
```

预期输出：

```
正在连接 WiFi...
状态码: 1000 状态码: 1000 
连接成功！
IP 地址等信息: ('192.168.1.105', '255.255.255.0', '192.168.1.1', '61.129.42.6')
```

其中，`wlan.ifconfig()` 返回的“IP 地址等信息”是一个四元组，顺序通常是：

```
(本机 IP, 子网掩码, 默认网关, DNS 服务器)
```

### 访问网络

连上网络后，就可以使用 `urequests` 库访问局域网或公网。下面是访问 `http://httpbin.org` 的例子：

```python
import urequests

try:
    response = urequests.get('http://httpbin.org/ip')
    print('状态码:', response.status_code)
    print('响应内容:', response.text)
    response.close()
except Exception as e:
    print('请求失败:', e)
```

完整代码见 [`esp32.py`](esp32.py) 。