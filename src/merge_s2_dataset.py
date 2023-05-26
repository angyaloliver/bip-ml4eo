"""
Merge the Sentinel-2 raster tiles.

Parameters:
    ROOT: the path of the root directory containing tiles.
    OUT_ROOT: the path of the output root directory.
"""

import re
from itertools import groupby
from pathlib import Path
from typing import Generator, Iterable, Literal, Optional, Sequence

import numpy as np
import rasterio
from rasterio.merge import merge
from tqdm import tqdm

ROOT = "data/Water/sentinel-2-cremona/images"
OUT_ROOT = "data/Water/sentinel-2-cremona/merged-images/"


S2_TILE_FILENAME_PATTERN = re.compile(
    r"^S2(A|B)_MSIL2A_(\d{8}T\d{6})_N(\d{4})_R(\d{3})_T([A-Z0-9]{5})_(\d{8}T\d{6})\.(\w+)$"
)


def parse_s2_tile_filename(path: Path) -> tuple[str, str, str, str, str, str]:
    """
    Parse Sentinel-2 level-2A products filenames.
    Names should follow the [Sentinel naming convention](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/naming-convention)
    """
    name = path.name
    match = S2_TILE_FILENAME_PATTERN.match(name)
    try:
        (
            mission_id,
            datatake_time,
            processing_baseline,
            relative_orbit,
            tile_id,
            other_time,
            format,
        ) = match.groups()  # type: ignore[union-attr]
    except AttributeError as exc:  # match is None
        raise ValueError(
            f"file name at '{str(path)}' does not follow Sentinel-2 tile naming correctly"
        ) from exc

    return mission_id, datatake_time, processing_baseline, relative_orbit, tile_id, other_time, format  # type: ignore[return-value]


def group_s2_tiles(paths: Iterable[Path]) -> list[list[Path]]:
    """Groups tiles by datatake information."""

    def sort_func(path):
        (
            mission_id,
            datatake_time,
            processing_baseline,
            relative_orbit,
            tile_id,
            other_time,
            format,
        ) = parse_s2_tile_filename(path)
        return (
            mission_id,
            datatake_time,
            processing_baseline,
            relative_orbit,
            other_time,
            format,
            tile_id,
        )

    def group_func(path):
        (
            mission_id,
            datatake_time,
            processing_baseline,
            relative_orbit,
            tile_id,
            other_time,
            format,
        ) = parse_s2_tile_filename(path)
        return (
            mission_id,
            datatake_time,
            processing_baseline,
            relative_orbit,
            other_time,
            format,
        )

    paths = sorted(paths, key=sort_func)
    return [list(tiles_group) for key, tiles_group in groupby(paths, key=group_func)]


def get_merged_tile_name(input_tile_name: str) -> str:
    return re.sub(
        S2_TILE_FILENAME_PATTERN,
        r"S2\1_MSIL2A_\2_N\3_R\4_merged_\6.\7",
        input_tile_name,
    )


def copy_nanmin(merged_data, new_data, merged_mask, new_mask, **kwargs):
    """
    Returns the minimum value pixel (support min).
    Adapted from `rasterio.merge.copy_min`
    """
    mask = np.empty_like(merged_mask, dtype="bool")
    np.logical_or(merged_mask, new_mask, out=mask)
    np.logical_not(mask, out=mask)
    np.nanmin(
        [merged_data, new_data], axis=0, out=merged_data, where=mask, initial=np.inf
    )
    np.logical_not(new_mask, out=mask)
    np.logical_and(merged_mask, mask, out=mask)
    np.copyto(merged_data, new_data, where=mask, casting="unsafe")


def merge_s2_tiles(tiles_paths: Sequence[Path], out_root: Path) -> None:
    """Merge tiles by creating a mosaic and output to a file."""

    # open raster files in DatasetReader objects
    src_files = [
        rasterio.open(tile_path, "r+", masked=True) for tile_path in tiles_paths
    ]
    # hack: overwrite the nodata field to np.nan
    # otherwise the merge method will consider NaN values as valid pixels and copy them
    # source: https://gis.stackexchange.com/a/427651
    for file in src_files:
        file.nodata = np.nan

    # set output path
    out_filename = get_merged_tile_name(tiles_paths[0].name)
    out_path = out_root / out_filename

    # merge tiles to create a mosaic
    merge(src_files, method="first", dst_path=out_path)


def get_s2_tiles_paths(root: Path) -> Generator[Path, None, None]:
    """Get the path to S2 tiles in root directory."""
    for path in root.iterdir():
        try:
            parse_s2_tile_filename(path)
        except ValueError:
            continue
        else:
            yield path


def merge_s2_dataset(root: Path, out_root: Optional[Path] = None) -> None:
    """Merge all tiles in the root folder and output to a folder."""
    if out_root is None:
        out_root = root.with_name("merged-" + root.name)
    try:
        out_root.mkdir()
    except FileExistsError:
        pass
    s2_tiles_paths = list(get_s2_tiles_paths(root))
    print(
        "{n} Sentinel-2 tiles paths found:\n{lines}".format(
            n=len(s2_tiles_paths), lines="\n".join(map(str, s2_tiles_paths))
        )
    )

    tiles_paths_groups = group_s2_tiles(get_s2_tiles_paths(root))

    for tiles_paths in tqdm(tiles_paths_groups):
        merge_s2_tiles(tiles_paths, out_root)


def main() -> None:
    """Main function of module."""
    root = Path(ROOT)
    out_root = None
    if OUT_ROOT is not None:
        out_root = Path(OUT_ROOT)

    merge_s2_dataset(root, out_root)


if __name__ == "__main__":
    main()
