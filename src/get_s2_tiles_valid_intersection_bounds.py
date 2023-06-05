"""
Get the bounds of the intersection of valid regions of 2 Sentinel-2 tiles.
"""

from pathlib import Path
from typing import TypeAlias

import numpy as np
import rasterio
from rasterio.io import DatasetReader
from rasterio import features

import shapely
from shapely.geometry import box, shape

ROOT = "data/Water/sentinel-2-cremona/images"
TILE_NAME_1 = "S2B_MSIL2A_20220307T101759_N0400_R065_T32TNQ_20220307T133430.tif"
TILE_NAME_2 = "S2B_MSIL2A_20220307T101759_N0400_R065_T32TNR_20220307T133430.tif"

Bounds: TypeAlias = tuple[float, float, float, float]


def get_valid_bounds(src: DatasetReader) -> Bounds:
    """
    Get the bounds of the smallest polygon encompassing all the valid values in the raster,
    excluding any nodata value.
    """
    # read nodata mask of first band
    # note: assumes the nodata pixels are shared across all bands which is the case here
    valid_mask = src.read_masks(1)
    # extract shapes from mask
    shapes = features.shapes(valid_mask, transform=src.transform)
    # extract the bounds of the shape that represent the valid region
    valid_polygons = [shape(geom) for geom, val in shapes if val]
    valid_polygon = shapely.union_all(valid_polygons)

    return valid_polygon.bounds


def get_s2_tiles_valid_intersection_bounds(tile_path_1: Path, tile_path_2: Path) -> Bounds:

    with rasterio.open(tile_path_1, "r+") as src_1, rasterio.open(tile_path_2, "r+") as src_2:
        # hack: overwrite the nodata field to np.nan
        # otherwise the merge method will consider NaN values as valid pixels and copy them
        # source: https://gis.stackexchange.com/a/427651
        src_1.nodata = np.nan
        src_2.nodata = np.nan

        # get valid bounds for the 2 tiles
        valid_bounds_1 = box(*get_valid_bounds(src_1))
        valid_bounds_2 = box(*get_valid_bounds(src_2))
        # get intersection of valid bounds
        intersection = valid_bounds_1.intersection(valid_bounds_2)

    return intersection.bounds


def main() -> None:

    root = Path(ROOT)
    tile_path_1 = root / TILE_NAME_1
    tile_path_2 = root / TILE_NAME_2

    bounds = get_s2_tiles_valid_intersection_bounds(tile_path_1, tile_path_2)
    print(bounds)


if __name__ == "__main__":

    main()
