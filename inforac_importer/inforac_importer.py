from datetime import datetime
import glob
import json
from pathlib import Path
import sys
import geopandas as gpd
import pandas as pd
import logging
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime, Boolean, Text
from sqlalchemy import select
import argparse
from sqlalchemy.orm import Session
import pycountry

"""
To be done in infomapnode db:

CREATE TABLE public.inforac_importer_log (
	id serial4 NOT NULL,
	processed_file varchar(250) NOT NULL,
	import_date_time timestamptz NOT NULL,
	successful bool NULL,
	logs text NULL,
	CONSTRAINT inforac_importer_log_pkey PRIMARY KEY (id)
);
GRANT ALL ON ALL TABLES IN SCHEMA public TO infomapnode;
GRANT USAGE, SELECT ON SEQUENCE inforac_importer_log_id_seq TO infomapnode;

"""

logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


Base = declarative_base()


class InfoRacImporterLog(Base):
    __tablename__ = "inforac_importer_log"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True)
    processed_file = Column(String, nullable=False)
    import_date_time = Column(DateTime, nullable=False)
    successful = Column(Boolean, nullable=True, default=None)
    logs = Column(Text, nullable=True)


def import_data(input_file_path):
    engine_geonode_data = create_engine(
        os.getenv("GEODATABASE_URL").replace("postgis", "postgresql"), echo=False
    )
    engine_geonode = create_engine(
        os.getenv("DATABASE_URL").replace("postgis", "postgresql"), echo=False
    )

    process_date = datetime.now()
    logger.info("Starting import processing")
    # checking path existance
    if not input_file_path:
        _log = "No input path was provided"
        logger.error(_log)
        raise Exception(_log)

    if not os.path.exists(input_file_path):
        _log = "Input path does not exists"
        logger.error(_log)
        raise Exception(_log)
    # reading configuration from path
    _json_conf_path = get_json_config_path()
    logger.info(f"loading configuration file: {_json_conf_path}")
    if not os.path.exists(_json_conf_path):
        raise Exception("Configuration path does not exists")

    try:
        with open(_json_conf_path) as f:
            _json_conf = json.loads(f.read())
    except:
        raise Exception("Configuration file is not a JSON")

    logger.info("checking if the logtable exists, otherwise we will create it")
    with Session(engine_geonode):
        has_table = inspect(engine_geonode).has_table(InfoRacImporterLog.__tablename__)
        if not has_table:
            logger.info("Table does not exists, creating...")
            InfoRacImporterLog.__table__.create(engine_geonode)
            logger.info("Table created")

    # start file loop
    for xlsx_file in glob.iglob(f"{input_file_path}/**/*.xlsx", recursive=True):
        # opening sqlachemy session. this is going to be open/close for every file
        with Session(engine_geonode) as session:
            logger.info(f"Starting processing of: {xlsx_file}")
            logger.info(f"Checking if file {xlsx_file} is available in the log table")
            # check if the log entry is already present in the log table
            exists = check_log_table_exists(xlsx_file, session)
            # evaluates the re-import of the file
            if any(exists):
                logger.info("Entry exists, evaluate of re-import")
                _log_obj = exists[0]
                _log_millis = _log_obj.import_date_time.timestamp() * 1000
                _file_millis = os.path.getmtime(xlsx_file) * 1000
                if _log_millis >= _file_millis:
                    logger.info(
                        "Last processing date is newer than the last modification date, skipping..."
                    )
                    continue
                else:
                    logger.info(
                        "The file is newer than the last execution date, reprocessing..."
                    )
                    _log_obj.import_date_time = process_date
                    _log_obj.successful = None
                    _log_obj.logs = None
                    session.commit()
            else:
                logger.info("Entry not found in log table, adding it")
                _log_obj = InfoRacImporterLog(
                    processed_file=xlsx_file, import_date_time=process_date
                )
                session.add(_log_obj)
                session.commit()

            code = Path(xlsx_file).stem.split("_")[0]

            config = _json_conf.get(code)
            # start looping on each sheet declared in the config file
            try:
                gdf = prepare_gpkg(xlsx_file, config)
                # saving data to postgis in append mode
            except Exception as e:
                logger.error(e)
                error = e
                continue
            finally:
                if isinstance(gdf, gpd.GeoDataFrame) and not gdf.empty:
                    logger.info("Dropping duplicates line before saving...")
                    gdf.drop_duplicates(inplace=True)

                    logger.info("Saving data in postgis table...")

                    gdf.to_postgis(
                        name=config.get("output_table", code).lower(),
                        con=engine_geonode_data,
                        if_exists="append",
                        index=False,
                        chunksize=1000,
                    )
                    logger.info("Data saved")

                logger.info("Updating status...")
                _log_obj.successful = True
                if error:
                    _log_obj.logs = str(error)
                    _log_obj.successful = False
                session.commit()
                logger.info("Status updated")


def prepare_gpkg(xlsx_file, config):
    gdf = gpd.GeoDataFrame()
    for sheet in config.get("sheet", []):
        error = None
        logger.info(f"Extracting data from sheet: {sheet}")
        cols_to_extract = config.get("columns", ["CountryCode"]) + config.get(
            "geom", []
        )
        df = pd.read_excel(xlsx_file, sheet, usecols=cols_to_extract or None)
        df["filename"] = os.path.basename(xlsx_file)
        # removing duplicates
        df.drop_duplicates(inplace=True)
        # converting country code in full name
        df["CountryCode"] = df["CountryCode"].apply(
            lambda x: pycountry.countries.get(alpha_2=x).name
        )
        # getting lan-lon from configuration
        lat, lon = config.get("geom", [])
        logger.info(f"Reading Geometry")
        # generation of geodataframe do handle the coordinates
        if gdf.empty:
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df[lon], df[lat]),
                crs="EPSG:4326",
            ).drop(columns=config.get("geom", []))
        else:
            # if we already have a GeoDataframe defined, measn
            # that we need to handle multiple sheet
            # we join them so we can keep all the data
            gdf = pd.concat(
                [
                    gdf,
                    gpd.GeoDataFrame(
                        df,
                        geometry=gpd.points_from_xy(df[lon], df[lat]),
                        crs="EPSG:4326",
                    ).drop(columns=config.get("geom", [])),
                ]
            )

    return gdf


def get_json_config_path():
    _json_conf_path = f"{os.path.dirname(__file__)}/inforac_mapping.json"
    return _json_conf_path


def check_log_table_exists(xlsx_file, session):
    statement = select(InfoRacImporterLog).where(
        InfoRacImporterLog.processed_file == xlsx_file
    )
    exists = False
    exists = [row for row in session.scalars(statement)]
    return exists


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="InfoRac importer",
        description="Read xlsx file and import them in geonode_data",
        usage="python inforac_importer.py /input/where/the/file/are/stored.xlsx",
        allow_abbrev=False,
    )

    parser.add_argument(
        "--noinput",
        "--no-input",
        action="store_false",
        dest="confirmation",
        help=("skips prompting for confirmation."),
    )

    parser.add_argument(
        "input_path",
        type=str,
        default=None,
        help="Input path where the XLSX file are located",
    )

    args = parser.parse_args()

    if not args.confirmation:
        import_data(args.input_path)
    else:
        overwrite_env = input(
            "This action will apped data for the available files. Do you wish to continue? (y/n)"
        )
        if overwrite_env not in ["y", "n"]:
            logger.error("Please enter a valid response")
        if overwrite_env == "y":
            import_data(args.input_path)
