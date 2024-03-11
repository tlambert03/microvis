"""Skip canvas creation."""

from imageio.v3 import imread

from microvis import View

view = View()

view.show()
view.add_image(imread("imageio:camera.png"))

if __name__ == "__main__":
    from qtpy.QtWidgets import QApplication

    app = QApplication([])
    app.exec_()
