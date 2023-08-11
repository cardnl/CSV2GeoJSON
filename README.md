# CSV2GeoJSON

Converts a CSV file to a GeoJSON FeatureCollection.

## Arguments

```
CSV2GeoJSON [-h] input output
                   [--long [LONG]] [--lat [LAT]]
                   [--bounds [BOUNDS]] [--dumpCSV DUMPCSV]
```

* `input` - An input CSV file with `longitude`, `latitude` columns.
* `output` - A output GeoJSON file.

### Optional arguments

* `--long` - Column which contains longitude data (`longitude` by default).
   *  e.g.: If your longitude data is in the `lng` column, use: `--long lng`
* `--lat` - Column which contains latitude data (`latitude` by default).
   *  e.g.: If your longitude data is in the `lng` column, use: `--long lat`
* `--bounds` - Expects [GeoBoundaries data](https://github.com/wmgeolab/geoBoundaries), adds a `_geo_admin` columns to the CSV data. 
   * See **Examples** for more information.
* `--dumpCSV` - Output file containing any modifications to the CSV data made by `--bounds`.
   *  e.g.: To dump CSV data, use: `--dumpCSV output.csv`


## Examples

### Basic Usage:  

If there is a file named `example.csv` containing:
```
title,name,height,latitude,longitude
mr,apple,7.65,42.589167,-83.371667
mrs,pear,7.75,29.563273,-95.286204
dr,orange,7.5,33.787892,-117.853136
```

|title|name|height|latitude|longitude|
|-|-|-|-|-|
|mr|apple|7.65|42.589167|-83.371667|
|mrs|pear|7.75|29.563273|-95.286204|
|dr|orange|7.5|33.787892|-117.853136|

Then executing:

```
./csv2geojson.py example.csv output.geojson
```

Would produce the file `output.geojson` containing:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "title": "mr",
        "name": "apple",
        "height": "7.65",
        "latitude": "42.589167",
        "longitude": "-83.371667"
      },
      "geometry": {
        "coordinates": [
          -83.371667,
          42.589167
        ],
        "type": "Point"
      }
    },
    ...
```

### Using GeoBoundaries

For linking [GeoBoundaries data](https://github.com/wmgeolab/geoBoundaries) to the CSV & GeoJSON file.

#### Step 1:
Obtain `geoBoundaries-USA-ADM#.geojson` from [GeoBoundaries USA folder](`https://github.com/wmgeolab/geoBoundaries/tree/main/releaseData/gbOpen`), and save them as:
* `ADM0.geojson`
* `ADM1.geojson`
* `ADM2.geojson`

#### Step 2:

Running:
```
./csv2geojson.py example.csv output.geojson --bounds=ADM0.geojson,ADM1.geojson,ADM2.geojson
```

Would produce the file `output.geojson` containing:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "title": "mr",
        "name": "apple",
        "height": "7.65",
        "latitude": "42.589167",
        "longitude": "-83.371667",
        "_geo_admin0": "United States",
        "_geo_admin1": "Michigan",
        "_geo_admin2": "Oakland"
        ...
```

#### Step 4:

Adding `--dumpCSV output.csv` would produce the CSV:

```
title,name,height,latitude,longitude,_geo_admin0,_geo_admin1,_geo_admin2
mr,apple,7.65,42.589167,-83.371667,United States,Michigan,Oakland
mrs,pear,7.75,29.563273,-95.286204,United States,Texas,Brazoria
dr,orange,7.5,33.787892,-117.853136,United States,California,Orange
```

|title|name|height|latitude|longitude|_geo_admin0|_geo_admin1|_geo_admin2|
|-|-|-|-|-|-|-|-|
|mr|apple|7.65|42.589167|-83.371667|United States|Michigan|Oakland|
|mrs|pear|7.75|29.563273|-95.286204|United States|Texas|Brazoria|
|dr|orange|7.5|33.787892|-117.853136|United States|California|Orange|
