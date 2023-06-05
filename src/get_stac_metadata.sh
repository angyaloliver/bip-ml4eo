#!/usr/bin/env bash

STAC_API_URL=https://earth-search.aws.element84.com/v1

out_file_1='data/Water/s2a-cremona-all-items.json'
# S2 level-2 A products over Cremona over period of interest
stac-client search ${STAC_API_URL} -c sentinel-2-l2a --bbox 9.8388880 45.0141297 10.1033520 45.1587585 --datetime 2022-03-07/2022-08-24 --save "${out_file_1}"

echo "S2 level-2-A products over Cremona over period of interest (saved at '${out_file_1})"
stacterm cal --label platform < "${out_file_1}"


out_file_2='data/Water/s2a-cremona-all-items-cloud-cover-lt-10.json'
# S2 level-2 A products over Cremona over period of interest filtered by cloud cover less than 10%
stac-client search ${STAC_API_URL} -c sentinel-2-l2a --bbox 9.8388880 45.0141297 10.1033520 45.1587585 --datetime 2022-03-07/2022-08-24 --query "eo:cloud_cover<10" --save "${out_file_2}"

echo ""
echo "S2 level-2-A products over Cremona over period of interest filtered by cloud cover less than 10% (saved at '${out_file_2})"

stacterm cal --label platform < "${out_file_2}"
