import time
import cv2 as cv
import mini_six as six

from mini_six import subscribe, DataSourceType, SubscribeData
from mini_six.portable.win32.observer import ScreenshotObserver

data_source = subscribe(source_type_dict={DataSourceType.IMAGE: ScreenshotObserver}, device_id_iter=0x10010)


@data_source(priority=2)
def action_1(data: SubscribeData):
    cv.imshow("action_1", data.image)
    cv.waitKey()
    print("normal function 1 working:")
    time.sleep(5)


@data_source(priority=1)
def action_2(data: SubscribeData):
    cv.imshow("action_2", data.image)
    cv.waitKey()
    print("normal function 2 working:")
    time.sleep(5)


six.run()
