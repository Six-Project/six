import mini_six as six
import cv2 as cv

six.init()


@six.watch(six.DataSource.SCREENSHOT, 0x10010, period=100)
def action(image):
    cv.imshow("hello six", image)
    cv.waitKey()
    cv.destroyAllWindows()


six.run()
