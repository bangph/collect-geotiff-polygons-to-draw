import gdal
from gdalconst import GA_ReadOnly
import sys
import glob
import os
import logging as log

### Configuration for logging task
logFormatter = log.Formatter("%(asctime)s %(message)s")
rootLogger = log.getLogger()

consoleHandler = log.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

rootLogger.setLevel(log.INFO)

script_dir = os.path.dirname(os.path.realpath(__file__));


if len(sys.argv) != 2:
    log.info("Usage: python scrip.py PATH_TO_FOLDER_CONTAINING_TIFF_FILES")
    exit(0)

input_dir = sys.argv[1]

if not os.path.exists(input_dir):
    log.error("Input folder does not exist, given '" + input_dir + "'.")
    exit(1)

tiff_files = glob.glob(input_dir + "/*.tif*")

i = 1

result = "";

features = [];

center_point = ""

for tiff_file in tiff_files:
    data = gdal.Open(tiff_file, GA_ReadOnly)
    geoTransform = data.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * data.RasterXSize
    miny = maxy + geoTransform[5] * data.RasterYSize
    data = None

    result += """var points{} = [[ [{}, {}], [{}, {}], [{}, {}], [{}, {}] ]];
var square{} = new ol.geom.Polygon(points{});
var squareFeature{} = new ol.Feature(square{});

""".format(i, minx, maxy, maxx, maxy, maxx, miny, minx, miny, i, i, i, i)

    features.append("squareFeature" + str(i))

    if i == 1:
        center_point = "[" + str((minx + maxx) / 2) + ", " + str((miny + maxy) / 2) + "]"

    log.info("Processing file: '{}'...".format(tiff_file))

    i += 1

str_features = ", ".join(features)

final_result = result + """
var source = new ol.source.Vector({
                                    features: [""" + str_features + """]
                                 });\n"""

final_result += "var center_point = {};".format(center_point);

with open(script_dir + "/app.js.in") as f:
    newText = f.read().replace("$GENERATED_CODE", final_result)

with open(script_dir + "/app.js", "w") as f:
    f.write(newText)
