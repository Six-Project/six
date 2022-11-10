import mini_six as six
import cv2 as cv

from mini_six import look, DataSource, Image

six.init()


@look(DataSource.SCREENSHOT, 0x10010, period=100)
def action(image: Image):
    cv.imshow("hello six", image.data)
    cv.waitKey()
    cv.destroyAllWindows()


six.run()
