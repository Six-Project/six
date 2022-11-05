# SIX 操作手册

## Hello World

### 安装 six

```shell
pip install mini-six
```

### 获取 six-demo

```shell
git clone https://github.com/Six-Project/six-demo.git
```

### 运行

进入项目目录，并运行

```shell
python run.py
```

## 介绍

### 入口文件 `run.py`

```python
import mini_six as six

six.init()  # 初始化
six.load_plugin("plugins", "hello")  # 加载插件：其中 plugins 是插件模块的路径，支持绝对路径和相对路径，hello 是插件名称
six.run()  # 运行

```

### 自定义插件

#### 什么是插件

此处的**插件**是指带有`__init__.py`的文件夹，**加载插件**是指执行插件中的`__init__.py`文件。

#### 插件里要些啥

插件里需要定义**Action**。

#### 什么是Action

Action 是一个 python 函数，它定义了在接收到**源数据流**后的一系列操作。

#### 什么是源数据流

1. 源数据流是指 action 订阅**源数据流接口**后获得的数据流。
2. **源数据流接口**是指由 six 适配各种 I/O 设备后给插件开发者提供的数据流接口。
3. Action 订阅对应的设备后，**无需其他请求**即可获取源数据流。
4. 目前支持以下源数据流接口。

| 源数据流 | 订阅方式                                          | 适配平台    |
|------|-----------------------------------------------|---------|
| 窗口截图 | `@six.watch("screenshot", handler, period=100)` | win32 ✅ |

#### 如何定义Action

```python
"""
定义 action 的示例代码
"""
import mini_six as six
import cv2 as cv


@six.watch(six.DataSource.SCREENSHOT, 0x10010, period=100)
def action(image):
    """
    1. 为什么要写 "six_python.watch" 以及为什么要设置形参 "image"？

    在函数上添加一行 @six_python.watch(six.DataSource.SCREENSHOT, 0x10010,period=100)
    表示该函数订阅了 0x10010 号设备的 screenshot 内容，且每过 100 个观察周期（默认 1 个观察周期
    的值为 5 个时钟周期，时钟周期为 10ms 左右，暂时无法精确）接收一次数据，需要用形参 image 去接收
    该订阅内容。
    
    2. action 在什么时候执行？
    当 0x10010 设备的 screenshot 信息更新时，调度系统会按一定的顺序调用 action。

    3. 是否允许多个 action 订阅一个信息源？
    是的。

    4. 订阅同一个信息源的多个 action 执行的顺序是怎么样的？
    默认是写在前面的 action 优先执行。
    
    5. 如何定义动作的频率？
    通过 period 参数定义

    参数：
        image：接收到的订阅内容
    """
    cv.imshow("hello mini-six", image)
    cv.waitKey()
    cv.destroyAllWindows()

```

#### 定义局部环境变量

1. 在插件内定义的环境变量存储在插件的命名空间
2. 在插件内获取环境变量时优先查找自身命名空间
3. 若查找不到，则继续查找全局

```python
"""
定义局部环境变量的示例代码
"""

import mini_six as six

config = six.Config()
LOCAL_CONFIG = {
    "static_path": "static/hello"
}
config.add(LOCAL_CONFIG)
```

#### 使用输入接口

| 接口用途     | 函数名                                   | 适配平台    |
|----------|---------------------------------------|---------|
| 按下键盘按键   | `six.operation.press_key`             | win32 ✅ |
| 松开键盘按键   | `six.operation.release_key`           | win32 ✅ |
| 单击键盘按键   | `six.operation.click_key`             | win32 ✅ |
| 单击键盘组合键 | `six.operation.click_combination_key` | win32 ✅ |
| 移动鼠标     | `six.operation.move_to`               | win32 ✅ |
| 按下鼠标左键   | `six.operation.left_down`             | win32 ✅ |
| 松开鼠标左键   | `six.operation.left_up`               | win32 ✅ |
| 上滚鼠标滚轮   | `six.operation.scroll_up`             | win32 ✅ |
| 下滚鼠标滚轮   | `six.operation.scroll_down`           | win32 ✅ |
| 下滚鼠标滚轮   | `six.operation.scroll_down`           | win32 ✅ |
| 在某处鼠标滚轮  | `six.operation.scroll`                | win32 ✅ |

```python
"""
使用输入接口的示例代码
"""

import mini_six as six

six.operation.press_key(0x10010, six.KEYMAP.VK_SPACE)  # 按下空格键
six.operation.release_key(0x10010, six.KEYMAP.VK_SPACE)  # 松开空格键

```