import os
import logging
import unittest
from inforac_importer import import_data
from unittest.mock import patch
from inforac_importer import import_data, prepare_gpkg
import geopandas as gpd

logging.disable(logging.INFO)


class TestInforacImporter(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_path = f"{os.path.dirname(__file__)}/test_data/"
        cls.single_file = f"{cls.input_path}/M1_for_unittest.xls"
        super().setUpClass()

    def test_given_invalid_path_should_raise_exception(self):
        with self.assertRaises(Exception):
            import_data(None)

    def test_given_not_existing_path_should_raise_exception(self):
        with self.assertRaises(Exception):
            import_data("/not/existing/path")

    @patch("inforac_importer.get_json_config_path")
    def test_given_non_existing_config_json_should_raise_exception(self, mocked_path):
        mocked_path.return_value = "/not/existing/path"
        with self.assertRaises(Exception):
            import_data(self.input_path)

    @patch("inforac_importer.get_json_config_path")
    def test_given_not_json_config_file_should_raise_exception(self, mocked_path):
        mocked_path.return_value = (
            f"{os.path.dirname(__file__)}/test_data/not_a_json.txt"
        )
        with self.assertRaises(Exception):
            import_data(self.input_path)

    @patch.dict(
        os.environ, {"GEODATABASE_URL": "mytemp", "DATABASE_URL": "url_db"}, clear=True
    )
    def test_prepare_gpkg_function(self):
        json_conf = {
            "sheet": ["Stations"],
            "geom": ["Latitude", "Longitude"],
            "columns": ["CountryCode"],
        }

        gdf = prepare_gpkg(self.single_file, json_conf)
        # check that a dataframe is returned
        self.assertIsInstance(gdf, gpd.GeoDataFrame)
        # check that the duplcate are removed (there are 3 rows in the File)
        self.assertFalse(gdf.is_empty.all())
        self.assertEqual(len(gdf), 2)
        # sanity check on the data extracted
        self.assertListEqual(
            ["CountryCode", "filename", "geometry"], gdf.columns.values.tolist()
        )
        # checking country converted
        self.assertEqual(["Italy", "Germany"], gdf["CountryCode"].values.tolist())
        # checking filename
        self.assertTrue("M1_for_unittest.xls" in gdf["filename"].unique())
        # validate geometry
        self.assertTrue(gdf.geometry.is_valid.all())


if __name__ == "__main__":
    unittest.main()
