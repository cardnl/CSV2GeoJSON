#!/usr/bin/env python3

"""Convert CSV rows to GeoJSON markers."""

import argparse
import csv
import json
import numpy as np
import shapely
import shapely.ops

class GeoBoundary:
    """Find a point within a collection of GeoJSON polygon."""


    def __init__(self, file_path):
        """Accept a GeoJSON FeatureCollection of polygons as boundaries"""
        with open(file_path, "r") as file:
            self.data = json.loads(file.read())

        self.places = self.data["features"]
        self.shapes = [self.__to_shape(feature) for feature in self.places]


    @staticmethod
    def __to_shape(feature):
        """Convert a GeoJSON feature to a Shapely shape"""
        return shapely.geometry.shape(feature["geometry"])


    @staticmethod
    def __haversine(pt1, pt2):
        """Use the haversine formula from:
           http://www.movable-type.co.uk/scripts/latlong.html"""
        [lng1, lat1, lng2, lat2] = map(np.deg2rad, [pt1.x, pt1.y, pt2.x, pt2.y])
        dlat = lat2 - lat1
        dlng = lng2 - lng1

        sindlat2 = np.power(np.sin(dlat / 2), 2)
        sindlng2 = np.power(np.sin(dlng / 2), 2)
        coslat1 = np.cos(lat1)
        coslat2 = np.cos(lat2)

        alpha = sindlat2 + coslat1 * coslat2 * sindlng2
        return 6371 * 2 * np.arctan2(np.sqrt(alpha), np.sqrt(1-alpha))


    def find(self, point):
        """Find the closest feature in the feature collection"""
        point = shapely.geometry.Point(*point)
        search = [self.places[idx] for idx, i in enumerate(self.shapes) if i.contains(point)]

        # If no regions, fallback by finding closest boundary
        if len(search) == 0:
            nearests = [shapely.ops.nearest_points(i, point) for idx, i in enumerate(self.shapes)]
            distances = [self.__haversine(i[0], point) for i in nearests]
            return [self.places[distances.index(min(distances))]]
        return search


    def dumps(self):
        """Dump the feature collection input as a JSON string"""
        return json.dumps(self.data)

class DictCSV:
    """Basic CSV wrapper"""

    def __init__(self, file_path):
        """Accept a path to a CSV file"""
        with open(file_path) as file:
            reader = csv.reader(file)
            header = next(reader)
            table = np.array(list(reader))
            self.header = header
            self.rows = [dict(zip(header, i)) for i in table]
            self.cols = dict(zip(header, table.T))

    def get_rows_by_col(self, col, value):
        """Gets the rows whose column has a specific value"""
        return [row for row in self.rows if row[col] == value]

    def add_col(self, name):
        """Adds an empty column to the CSV file"""
        self.header.append(name)
        self.rows = [{**row, name: ""} for row in self.rows]
        self.cols[name] = ["" for _ in self.rows]

    def get_row(self, row_id):
        """Gets the row at row_id"""
        return self.rows[row_id]

    def set_row(self, row_id, row):
        """Sets the row at row_id"""
        self.rows[row_id] = row
        for k in self.header:
            self.cols[k][row_id] = row[k]

    def dump(self, file_path):
        """Dumps the modified CSV file"""
        with open(file_path, "w") as file:
            writer = csv.writer(file, lineterminator="\n")
            writer.writerows([self.header, *[row.values() for row in self.rows]])


class CSV2GeoJSON:
    """Converts a CSV file to list of GeoJSON markers"""

    def __init__(self, csv_file, long_col, lat_col, boundary_files):
        """Accept a CSV file, latitude & longitude column names & geoBoundaries file
           Boundary files must be of the form: https://github.com/wmgeolab/geoBoundaries"""

        self.boundaries = [GeoBoundary(i) for i in boundary_files]
        self.csv = DictCSV(csv_file)
        self.long_col = long_col
        self.lat_col = lat_col

        if len(boundary_files) == 0:
            return

        for level, boundary in enumerate(self.boundaries):
            col_name = f'_geo_admin{level}'
            self.csv.add_col(col_name)

            # Loop through each row
            for row_id, row in enumerate(self.csv.rows):
                point = [*map(float, [row[long_col], row[lat_col]])]

                # Find boundary corresponding to longitude & latitude
                region = boundary.find(point)[0]["properties"]["shapeName"]

                self.csv.set_row(row_id, {**row, col_name: region})

    def __to_feature(self, row):
        """Convert a row into a feature"""
        return {
            "type": "Feature",
            "properties": row,
            "geometry": {
                "coordinates": [
                    float(row[self.long_col]),
                    float(row[self.lat_col])
                ],
                "type": "Point"
            }
        }

    def dump_markers(self, file_path):
        """Dump data as GeoJSON markers"""
        with open(file_path, "w") as file:
            json.dump({
                "type": "FeatureCollection", "features": [
                    self.__to_feature(i) for i in self.csv.rows
                ]
            }, file)

    def dump_csv(self, file):
        """Dump data as CSV, if boundary_files were given, _geo_admin columns are added"""
        self.csv.dump(file)


def main():
    """Usage: csv2geojson.py [inputCSV] [outputJSON]
       e.g.:
       > csv2geojson usa.csv usa.geojson --bounds=ADM1.geojson,ADM2.geojson,ADM3.geojson
    """
    parser = argparse.ArgumentParser("CSV2GeoJSON")
    parser.add_argument("input", help="input CSV file with longitude, latitude columns", type=str)
    parser.add_argument("output", help="output file for GeoJSON markers", type=str)
    parser.add_argument("--dumpCSV", help="dump CSV with _geo_admin columns appended", type=str)
    parser.add_argument(
        "--bounds",
        help="list of wmgeolab/geoBoundaries ADM GeoJSON file.",
        nargs="?",
        type=str
    )
    parser.add_argument(
        "--long",
        help="name of the longitude column in the input CSV",
        type=str,
        nargs="?",
        default="longitude"
    )
    parser.add_argument(
        "--lat",
        help="name of the latitude column in the input CSV",
        type=str,
        nargs="?",
        default="latitude"
    )
    args = parser.parse_args()

    boundary_files = args.bounds.split(",") if args.bounds else []
    geojson = CSV2GeoJSON(args.input, args.long, args.lat, boundary_files)

    geojson.dump_markers(args.output)

    if args.dumpCSV:
        geojson.dump_csv(args.dumpCSV)

if __name__ == "__main__":
    main()
