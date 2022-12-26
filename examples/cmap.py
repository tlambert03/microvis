import sys
from functools import total_ordering
from typing import TYPE_CHECKING
from weakref import WeakSet

from imageio.v3 import imread

if TYPE_CHECKING:
    from matplotlib import colors


@total_ordering
class Colormap:
    _registry: WeakSet["Colormap"] = WeakSet()

    def __init__(self, name: str) -> None:
        self.name = name
        self._registry.add(self)
        mpl_reg(self)

    def to_mpl(self) -> "colors.Colormap":
        from matplotlib import colors

        # TODO:
        return colors.LinearSegmentedColormap(
            name=self.name,
            segmentdata={
                "red": [(0, 0, 0), (1, 1, 1)],
                "green": [(0, 0, 0), (1, 0, 0)],
                "blue": [(0, 0, 0), (1, 0, 0)],
            },
        )

    def __str__(self) -> str:
        return self.name

    def __lt__(self, other: str) -> bool:
        return self.name <= other


def mpl_reg(*cmaps: Colormap) -> None:
    """Register specified/all Colormap instances with matplotlib.

    This allows the Colormap instance *itself* to be passed as
    as the `cmap` argument to matplotlib functions.

    If no Colormap instances are specified, all Colormap instances
    in the registry are registered.

    This function does nothing if matplotlib is not already imported.
    """
    if mpl := sys.modules.get("matplotlib"):
        for cmap in cmaps or Colormap._registry:
            if cmap not in mpl.colormaps:
                mpl.colormaps.register(cmap.to_mpl(), name=cmap)


my_cmap = Colormap("my_cmap")
img_data = imread("imageio:camera.png")

viewer = "vispy"
if viewer == "matplotlib":
    import matplotlib.pyplot as plt

    mpl_reg()
    plt.imshow(img_data, cmap=my_cmap)
    plt.show()
elif viewer == "vispy":
    from vispy import app, scene

    canvas = scene.SceneCanvas(keys="interactive")
    canvas.size = 800, 600
    canvas.show()
    view = canvas.central_widget.add_view()
    view.camera = scene.PanZoomCamera(aspect=1)
    image = scene.visuals.Image(img_data, parent=view.scene)
    # flip y-axis to have correct aligment
    view.camera.flip = (0, 1, 0)
    view.camera.set_range()
    app.run()
