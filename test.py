import mini_six as six
import cv2 as cv

from mini_six import look, DataSource, Image, SubscribeMode

six.init()


@look(DataSource.SCREENSHOT, 0x10010, period=20, subscribe_mode=SubscribeMode.PULL)
def action(image: Image):
    cv.imshow("hello six", image.data)
    cv.waitKey()
    cv.destroyAllWindows()


six.run()
