#!/bin/bash

if [ $# -lt 4 ]; then
    echo "Usage: ./iconify_to_raw.sh <iconify-id> <size> <R> <G> <B>"
    exit 1
fi

ICON_ID="$1"
SIZE="$2"
R="$3"
G="$4"
B="$5"

SAFE_ID="${ICON_ID//:/_}"

SVG_FILE="${SAFE_ID}_${SIZE}_${R}_${G}_${B}.svg"
PNG_FILE="${SAFE_ID}_${SIZE}_${R}_${G}_${B}.png"
RAW_FILE="${SAFE_ID}_${SIZE}_${R}_${G}_${B}.raw"

# Load SVG
URL="https://api.iconify.design/${ICON_ID}.svg?height=${SIZE}"
echo "Loading Iconify SVG: $URL"
curl -s -o "$SVG_FILE" "$URL"

if [ ! -f "$SVG_FILE" ]; then
    echo "Error: SVG could not be loaded."
    exit 1
fi

echo "SVG saved: $SVG_FILE"

sed -i 's/<svg[^>]*>/&\n  <rect width="100%" height="100%" fill="black" \/>/' "$SVG_FILE"
sed -i "s/stroke=\"currentColor\"/stroke=\"rgb(${R},${G},${B})\"/g" "$SVG_FILE"
sed -i "s/stroke=\"#000\"/stroke=\"rgb(${R},${G},${B})\"/g" "$SVG_FILE"
sed -i "s/fill=\"currentColor\"/fill=\"rgb(${R},${G},${B})\"/g" "$SVG_FILE"



# SVG -> PNG (Color icon)
echo "Convert SVG -> PNG: $PNG_FILE"
convert "$SVG_FILE" -resize "${SIZE}x${SIZE}" PNG32:"$PNG_FILE"

if [ ! -f "$PNG_FILE" ]; then
    echo "Error: PNG could not be created."
    exit 1
fi

echo "PNG saved: $PNG_FILE"

# PNG -> RAW
echo "Convert PNG -> RAW (RGB565): $RAW_FILE"
python3 img2rgb565.py "$PNG_FILE"

echo "DONE -> RAW file created: $RAW_FILE"
cp $RAW_FILE ../src/icons/.
