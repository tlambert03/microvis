from typing import Union, Literal

ClimString = Literal["auto"]
ValidClim = Union[ClimString, tuple[float, float]]
ValidCmap = str