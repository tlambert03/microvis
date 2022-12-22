# mini proposal
# - raw data in the `Image` model is nD
# - from raw data `Image` *must* be able to yield stacked 3D `... c d h w`,
#   similar to pytorch data model but nD
# e.g.
#   - single 2D RGBA image `h w c -> ... c 1 h w`
#   - 2D intensity image `h w -> ... 1 1 h w`
#   - batched multichannel volume `b c d h w -> ... b c d h w`
# n.b. when viewed in 3D, an arbitrary reduction is performed over the channel dim


# unified space is 'c d h w'
import dataclasses


@dataclasses.dataclass
class World:
    ndim: int = 7
