from camera import Camera, PixelFormat, FrameSize
import jpeg

# 初始化摄像头
try:
    cam = Camera(
        data_pins=[11, 9, 8, 10, 12, 18, 17, 16],
        vsync_pin=6,
        href_pin=7,
        sda_pin=4,
        scl_pin=5,
        pclk_pin=13,
        xclk_pin=15,
        xclk_freq=20000000,
        powerdown_pin=-1,
        reset_pin=-1,
        pixel_format=PixelFormat.RGB565,
        frame_size=FrameSize.QVGA
    )
    print("摄像头初始化成功 (RGB565模式)")
except Exception as e:
    print("初始化失败:", e)
    raise SystemExit from e


# 捕获一帧
try:
    buf = cam.capture()
    if buf:
        # 创建编码器
        enc = jpeg.Encoder(
            width=320,
            height=240,
            pixel_format="RGB565_BE",   # 使用大端序 RGB565
            quality=85
        )
        # 调用编码器实例的 encode 方法
        jpeg_buf = enc.encode(buf)
        if jpeg_buf:
            with open('test.jpg', 'wb') as f:
                f.write(jpeg_buf)
            print("照片已保存为 test.jpg")
        else:
            print("JPEG 编码失败")
    else:
        print("捕获失败")
except Exception as e:
    print("捕获出错:", e)

# 释放摄像头
cam.deinit()
