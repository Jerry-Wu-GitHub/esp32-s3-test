# The main.py file on ESP32.

import network
import time
import urequests

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

    try:
        response = urequests.get('http://httpbin.org/ip')
        print('状态码:', response.status_code)
        print('响应内容:', response.text)
        response.close()
    except Exception as e:
        print('请求失败:', e)
else:
    print(f'\n连接失败，最终状态码: {wlan.status()}')
