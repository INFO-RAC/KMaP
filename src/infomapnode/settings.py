# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2017 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

# Django settings for the GeoNode project.
import os
import ast

try:
    from urllib.parse import urlparse, urlunparse
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request
    from urlparse import urlparse, urlunparse
# Load more settings from a file called local_settings.py if it exists
try:
    from infomapnode.local_settings import *
#    from geonode.local_settings import *
except ImportError:
    from geonode.settings import *

#
# General Django development settings
#
PROJECT_NAME = 'infomapnode'

# add trailing slash to site url. geoserver url will be relative to this
if not SITEURL.endswith('/'):
    SITEURL = '{}/'.format(SITEURL)

SITENAME = os.getenv("SITENAME", 'infomapnode')

# Defines the directory that contains the settings file as the LOCAL_ROOT
# It is used for relative settings elsewhere.
LOCAL_ROOT = os.path.abspath(os.path.dirname(__file__))

WSGI_APPLICATION = "{}.wsgi.application".format(PROJECT_NAME)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', "en")

LANGUAGES = (
    ('en-us', 'English'),
)

if PROJECT_NAME not in INSTALLED_APPS:
    INSTALLED_APPS += (PROJECT_NAME,)

# Location of url mappings
ROOT_URLCONF = os.getenv('ROOT_URLCONF', '{}.urls'.format(PROJECT_NAME))

# Additional directories which hold static files
# - Give priority to local geonode-project ones
STATICFILES_DIRS = [os.path.join(LOCAL_ROOT, "static"), ] + STATICFILES_DIRS

# Location of locale files
LOCALE_PATHS = (
    os.path.join(LOCAL_ROOT, 'locale'),
    ) + LOCALE_PATHS

TEMPLATES[0]['DIRS'].insert(0, os.path.join(LOCAL_ROOT, "templates"))
loaders = TEMPLATES[0]['OPTIONS'].get('loaders') or ['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader']
# loaders.insert(0, 'apptemplates.Loader')
TEMPLATES[0]['OPTIONS']['loaders'] = loaders
TEMPLATES[0].pop('APP_DIRS', None)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d '
                      '%(thread)d %(message)s'
        },
        'simple': {
            'format': '%(message)s',
        },
        "command": {
            "format": "%(levelname)-7s %(asctime)s - %(message)s"
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        "command": {
            "level": "DEBUG", "class": "logging.StreamHandler", "formatter": "command"},

    },
    "loggers": {
        "django": {
            "handlers": ["console"], "level": "ERROR", },
        "geonode": {
            "handlers": ["console"], "level": "INFO", },
        "geoserver-restconfig.catalog": {
            "handlers": ["console"], "level": "ERROR", },
        "owslib": {
            "handlers": ["console"], "level": "ERROR", },
        "pycsw": {
            "handlers": ["console"], "level": "ERROR", },
        "celery": {
            "handlers": ["console"], "level": "DEBUG", },
        "mapstore2_adapter.plugins.serializers": {
            "handlers": ["console"], "level": "DEBUG", },
        "geonode_logstash.logstash": {
            "handlers": ["console"], "level": "DEBUG", },
        "infomapnode.management": {
            "level": "DEBUG", "handlers": ["command"], "propagate": False},
        "infomapnode.fulltextsearch.management": {
            "level": "DEBUG", "handlers": ["command"], "propagate": False},
    },
}

CENTRALIZED_DASHBOARD_ENABLED = ast.literal_eval(os.getenv('CENTRALIZED_DASHBOARD_ENABLED', 'False'))
if CENTRALIZED_DASHBOARD_ENABLED and USER_ANALYTICS_ENABLED and 'geonode_logstash' not in INSTALLED_APPS:
    INSTALLED_APPS += ('geonode_logstash',)

    CELERY_BEAT_SCHEDULE['dispatch_metrics'] = {
        'task': 'geonode_logstash.tasks.dispatch_metrics',
        'schedule': 3600.0,
    }

LDAP_ENABLED = ast.literal_eval(os.getenv('LDAP_ENABLED', 'False'))
if LDAP_ENABLED and 'geonode_ldap' not in INSTALLED_APPS:
    INSTALLED_APPS += ('geonode_ldap',)

# Add your specific LDAP configuration after this comment:
# https://docs.geonode.org/en/master/advanced/contrib/#configuration

DEFAULT_MS2_BACKGROUNDS = [
    #{
    #    "type": "osm",
    #    "title": "Open Street Map",
    #    "name": "mapnik",
    #    "source": "osm",
    #    "group": "background",
    #    "visibility": False,
    #},
    {
        "format": "image/png",
        "name": "Hosted_basemap_inforac_3857",
        "description": "Hosted_basemap_inforac_3857",
        "style": "default",
        "title": "Hosted basemap inforac 3857",
        "type": "wmts",
        "group": "background",
        "url": "https://maps.info-rac.org:443/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS",
        "bbox": {
            "crs": "EPSG:4326",
            "bounds": {
                "minx": "-179.99999550841463",
                "miny": "-88.99999992161116",
                "maxx": "179.99999550841463",
                "maxy": "88.99999992161116"
            }
        },
        "allowedSRS": {
            "EPSG:3857": True
        },
        "requestEncoding": "KVP",
        "capabilitiesURL": "https://maps.info-rac.org/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",
        "availableTileMatrixSets": {
            "default028mm": {
                "crs": "EPSG:3857",
                "tileMatrixSetLink": "sources['https://maps.info-rac.org/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS/1.0.0/WMTSCapabilities.xml'].tileMatrixSet['default028mm']"
            },
            "GoogleMapsCompatible": {
                "crs": "EPSG:3857",
                "tileMatrixSetLink": "sources['https://maps.info-rac.org/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS/1.0.0/WMTSCapabilities.xml'].tileMatrixSet['GoogleMapsCompatible']"
            }
        },
        "matrixIds": [
          "default028mm",
          "GoogleMapsCompatible"
        ],
        "tileMatrixSet": True,
        "thumbURL": "https://maps.info-rac.org/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS?layer=Hosted_basemap_inforac_3857&style=default&tilematrixset=default028mm&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%2Fpng&TileMatrix=0&TileCol=0&TileRow=0",
        "visibility": True,
    },
    {
        "type": "tileprovider",
        "title": "OpenTopoMap",
        "provider": "OpenTopoMap",
        "name": "OpenTopoMap",
        "source": "OpenTopoMap",
        "group": "background",
        "visibility": False,
    },
#     {
#         "type": "wms",
#         "title": "Sentinel-2 cloudless - https://s2maps.eu",
#         "format": "image/jpeg",
#         "name": "s2cloudless:s2cloudless",
#         "url": "https://maps.geosolutionsgroup.com/geoserver/wms",
#         "group": "background",
#         "thumbURL": f"{SITEURL}static/mapstorestyle/img/s2cloudless-s2cloudless.png",
#         "visibility": False,
#     },
    {
        "group": "background",
        "source": "ol",
        "title": "Empty Background",
        "type": "empty",
        "singleTile": False,
        "dimensions": [],
        "hideLoading": False,
        "handleClickOnLayer": False,
        "useForElevation": False,
        "hidden": False,
        "visibility": False,
    },
]

MAPSTORE_BASELAYERS_SOURCES = {
    "https://maps.info-rac.org/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS/1.0.0/WMTSCapabilities.xml": {
        "tileMatrixSet": {
            "default028mm": {
                "ows:Title": "TileMatrix using 0.28mm",
                "ows:Abstract": "The tile matrix set that has scale values calculated based on the dpi defined by OGC specification (dpi assumes 0.28mm as the physical distance of a pixel).",
                "ows:Identifier": "default028mm",
                "ows:SupportedCRS": "urn:ogc:def:crs:EPSG::3857",
                "TileMatrix": [
                    {
                        "ows:Identifier": "0",
                        "ScaleDenominator": "5.59082264028501E8",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "1",
                        "MatrixHeight": "2"
                    },
                    {
                        "ows:Identifier": "1",
                        "ScaleDenominator": "2.7954113201425016E8",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "2",
                        "MatrixHeight": "3"
                    },
                    {
                        "ows:Identifier": "2",
                        "ScaleDenominator": "1.3977056600712565E8",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "4",
                        "MatrixHeight": "6"
                    },
                    {
                        "ows:Identifier": "3",
                        "ScaleDenominator": "6.988528300356229E7",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "8",
                        "MatrixHeight": "11"
                    },
                    {
                        "ows:Identifier": "4",
                        "ScaleDenominator": "3.494264150178117E7",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "16",
                        "MatrixHeight": "21"
                    },
                    {
                        "ows:Identifier": "5",
                        "ScaleDenominator": "1.7471320750890587E7",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "32",
                        "MatrixHeight": "41"
                    },
                    {
                        "ows:Identifier": "6",
                        "ScaleDenominator": "8735660.375445293",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "64",
                        "MatrixHeight": "81"
                    },
                    {
                        "ows:Identifier": "7",
                        "ScaleDenominator": "4367830.187722629",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "128",
                        "MatrixHeight": "161"
                    },
                    {
                        "ows:Identifier": "8",
                        "ScaleDenominator": "2183915.093861797",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "256",
                        "MatrixHeight": "322"
                    },
                    {
                        "ows:Identifier": "9",
                        "ScaleDenominator": "1091957.546930427",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "512",
                        "MatrixHeight": "643"
                    },
                    {
                        "ows:Identifier": "10",
                        "ScaleDenominator": "545978.773465685",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "1024",
                        "MatrixHeight": "1285"
                    },
                    {
                        "ows:Identifier": "11",
                        "ScaleDenominator": "272989.38673236995",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "2048",
                        "MatrixHeight": "2570"
                    },
                    {
                        "ows:Identifier": "12",
                        "ScaleDenominator": "136494.69336618498",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "4096",
                        "MatrixHeight": "5139"
                    },
                    {
                        "ows:Identifier": "13",
                        "ScaleDenominator": "68247.34668309249",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "8192",
                        "MatrixHeight": "10278"
                    },
                    {
                        "ows:Identifier": "14",
                        "ScaleDenominator": "34123.673341546244",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "16384",
                        "MatrixHeight": "20556"
                    },
                    {
                        "ows:Identifier": "15",
                        "ScaleDenominator": "17061.836671245605",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "32768",
                        "MatrixHeight": "41112"
                    },
                    {
                        "ows:Identifier": "16",
                        "ScaleDenominator": "8530.918335622784",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "65536",
                        "MatrixHeight": "82223"
                    },
                    {
                        "ows:Identifier": "17",
                        "ScaleDenominator": "4265.459167338928",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "131072",
                        "MatrixHeight": "164445"
                    },
                    {
                        "ows:Identifier": "18",
                        "ScaleDenominator": "2132.7295841419354",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "262144",
                        "MatrixHeight": "328889"
                    },
                    {
                        "ows:Identifier": "19",
                        "ScaleDenominator": "1066.364791598498",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "524288",
                        "MatrixHeight": "657777"
                    },
                    {
                        "ows:Identifier": "20",
                        "ScaleDenominator": "533.1823957992484",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "1048576",
                        "MatrixHeight": "1315553"
                    },
                    {
                        "ows:Identifier": "21",
                        "ScaleDenominator": "266.5911978996242",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "2097152",
                        "MatrixHeight": "2631106"
                    },
                    {
                        "ows:Identifier": "22",
                        "ScaleDenominator": "133.2955989498121",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "4194304",
                        "MatrixHeight": "5262212"
                    },
                    {
                        "ows:Identifier": "23",
                        "ScaleDenominator": "66.64779947490605",
                        "TopLeftCorner": "-2.0037508342787E7 2.0037508342787E7",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "8388608",
                        "MatrixHeight": "10524424"
                    }
                ]
            },
            "GoogleMapsCompatible": {
                "ows:Title": "GoogleMapsCompatible",
                "ows:Abstract": "the wellknown 'GoogleMapsCompatible' tile matrix set defined by OGC WMTS specification",
                "ows:Identifier": "GoogleMapsCompatible",
                "ows:SupportedCRS": "urn:ogc:def:crs:EPSG:6.18.3:3857",
                "WellKnownScaleSet": "urn:ogc:def:wkss:OGC:1.0:GoogleMapsCompatible",
                "TileMatrix": [
                    {
                        "ows:Identifier": "0",
                        "ScaleDenominator": "559082264.0287178",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "1",
                        "MatrixHeight": "1"
                    },
                    {
                        "ows:Identifier": "1",
                        "ScaleDenominator": "279541132.0143589",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "2",
                        "MatrixHeight": "2"
                    },
                    {
                        "ows:Identifier": "2",
                        "ScaleDenominator": "139770566.0071794",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "4",
                        "MatrixHeight": "4"
                    },
                    {
                        "ows:Identifier": "3",
                        "ScaleDenominator": "69885283.00358972",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "8",
                        "MatrixHeight": "8"
                    },
                    {
                        "ows:Identifier": "4",
                        "ScaleDenominator": "34942641.50179486",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "16",
                        "MatrixHeight": "16"
                    },
                    {
                        "ows:Identifier": "5",
                        "ScaleDenominator": "17471320.75089743",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "32",
                        "MatrixHeight": "32"
                    },
                    {
                        "ows:Identifier": "6",
                        "ScaleDenominator": "8735660.375448715",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "64",
                        "MatrixHeight": "64"
                    },
                    {
                        "ows:Identifier": "7",
                        "ScaleDenominator": "4367830.187724357",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "128",
                        "MatrixHeight": "128"
                    },
                    {
                        "ows:Identifier": "8",
                        "ScaleDenominator": "2183915.093862179",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "256",
                        "MatrixHeight": "256"
                    },
                    {
                        "ows:Identifier": "9",
                        "ScaleDenominator": "1091957.546931089",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "512",
                        "MatrixHeight": "512"
                    },
                    {
                        "ows:Identifier": "10",
                        "ScaleDenominator": "545978.7734655447",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "1024",
                        "MatrixHeight": "1024"
                    },
                    {
                        "ows:Identifier": "11",
                        "ScaleDenominator": "272989.3867327723",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "2048",
                        "MatrixHeight": "2048"
                    },
                    {
                        "ows:Identifier": "12",
                        "ScaleDenominator": "136494.6933663862",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "4096",
                        "MatrixHeight": "4096"
                    },
                    {
                        "ows:Identifier": "13",
                        "ScaleDenominator": "68247.34668319309",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "8192",
                        "MatrixHeight": "8192"
                    },
                    {
                        "ows:Identifier": "14",
                        "ScaleDenominator": "34123.67334159654",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "16384",
                        "MatrixHeight": "16384"
                    },
                    {
                        "ows:Identifier": "15",
                        "ScaleDenominator": "17061.83667079827",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "32768",
                        "MatrixHeight": "32768"
                    },
                    {
                        "ows:Identifier": "16",
                        "ScaleDenominator": "8530.918335399136",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "65536",
                        "MatrixHeight": "65536"
                    },
                    {
                        "ows:Identifier": "17",
                        "ScaleDenominator": "4265.459167699568",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "131072",
                        "MatrixHeight": "131072"
                    },
                    {
                        "ows:Identifier": "18",
                        "ScaleDenominator": "2132.729583849784",
                        "TopLeftCorner": "-20037508.34278925 20037508.34278925",
                        "TileWidth": "256",
                        "TileHeight": "256",
                        "MatrixWidth": "262144",
                        "MatrixHeight": "262144"
                    }
                ]
            }
        }
    }
}

if MAPBOX_ACCESS_TOKEN:
    BASEMAP = {
        "type": "tileprovider",
        "title": "MapBox streets-v11",
        "provider": "MapBoxStyle",
        "name": "MapBox streets-v11",
        "accessToken": f"{MAPBOX_ACCESS_TOKEN}",
        "source": "streets-v11",
        "thumbURL": f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/6/33/23?access_token={MAPBOX_ACCESS_TOKEN}",  # noqa
        "group": "background",
        "visibility": False,
    }
    DEFAULT_MS2_BACKGROUNDS = [
        BASEMAP,
    ] + DEFAULT_MS2_BACKGROUNDS

# if BING_API_KEY:
#     BASEMAP = {
#         "type": "bing",
#         "title": "Bing Aerial",
#         "name": "AerialWithLabels",
#         "source": "bing",
#         "group": "background",
#         "apiKey": "{{apiKey}}",
#         "visibility": False,
#     }
#     DEFAULT_MS2_BACKGROUNDS = [
#         BASEMAP,
#     ] + DEFAULT_MS2_BACKGROUNDS

MAPSTORE_BASELAYERS = DEFAULT_MS2_BACKGROUNDS

# OpenLDAP settings
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfUniqueNamesType
import logging

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

AUTHENTICATION_BACKENDS = (
    'infomapnode.backend.IMNLDAPBackend',
) + AUTHENTICATION_BACKENDS

AUTH_LDAP_SERVER_URI = os.getenv(
    'AUTH_LDAP_SERVER_URI', 'ldap://localhost:389'
)

AUTH_LDAP_BIND_DN = os.getenv(
    'AUTH_LDAP_BIND_DN', 'cn=admin,dc=example,dc=org'
)

AUTH_LDAP_BIND_PASSWORD = os.getenv(
    'AUTH_LDAP_BIND_PASSWORD', 'password'
)

AUTH_LDAP_USER_BASE_SEARCH = os.getenv(
    'AUTH_LDAP_USER_BASE_SEARCH', 'dc=example,dc=org'
)

AUTH_LDAP_USER_SEARCH_ATTR = os.getenv(
    'AUTH_LDAP_USER_SEARCH_ATTR', 'uid'
)

AUTH_LDAP_USER_SEARCH = LDAPSearch(
    AUTH_LDAP_USER_BASE_SEARCH,
    ldap.SCOPE_SUBTREE,
    "({}=%(user)s)".format(AUTH_LDAP_USER_SEARCH_ATTR),
)

DJANGO_USER_ATTR_1 = os.getenv('DJANGO_USER_ATTR_1', 'first_name')
LDAP_USER_ATTR_1 = os.getenv('LDAP_USER_ATTR_1', 'givenName')
DJANGO_USER_ATTR_2 = os.getenv('DJANGO_USER_ATTR_2', 'last_name')
LDAP_USER_ATTR_2 = os.getenv('LDAP_USER_ATTR_2', 'sn')
DJANGO_USER_ATTR_3 = os.getenv('DJANGO_USER_ATTR_3', 'email')
LDAP_USER_ATTR_3 = os.getenv('LDAP_USER_ATTR_3', 'mail')
DJANGO_USER_ATTR_4 = os.getenv('DJANGO_USER_ATTR_4', 'username')
LDAP_USER_ATTR_4 = os.getenv('LDAP_USER_ATTR_4', 'uid')

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    DJANGO_USER_ATTR_1: LDAP_USER_ATTR_1,
    DJANGO_USER_ATTR_2: LDAP_USER_ATTR_2,
    DJANGO_USER_ATTR_3: LDAP_USER_ATTR_3,
    DJANGO_USER_ATTR_4: LDAP_USER_ATTR_4,
}

AUTH_LDAP_ALWAYS_UPDATE_USER = ast.literal_eval(
    os.getenv(
        'AUTH_LDAP_ALWAYS_UPDATE_USER', 'True'
    )
)

#Set up the basic group parameters.
LDAP_GROUP_OBJECTCLASS = os.getenv(
    'LDAP_GROUP_OBJECTCLASS', '(objectClass=GroupOfUniqueNames)'
)
LDAP_GROUP_BASE_SEARCH = os.getenv(
    'LDAP_GROUP_BASE_SEARCH', 'ou=groups,dc=example,dc=org'
)

AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    LDAP_GROUP_BASE_SEARCH,
    ldap.SCOPE_SUBTREE,
    LDAP_GROUP_OBJECTCLASS
)

AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType(name_attr='cn')

LDAP_GROUP_STAFF_DN = os.getenv(
    'LDAP_GROUP_STAFF_DN', 'cn=staff,ou=groups,dc=example,dc=org'
)

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_staff": LDAP_GROUP_STAFF_DN,
}

AUTH_LDAP_MIRROR_GROUPS = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = ast.literal_eval(
    os.getenv(
        'AUTH_LDAP_FIND_GROUP_PERMS', 'True'
    )
)

# Use OU attribute to assign groups membership
IMN_AUTH_LDAP_OU_SEPARATOR = '|'
IMN_AUTHORIZE_USERS_FROM_OU = True

ENABLE_SUBSITE_CUSTOM_THEMES = True

INSTALLED_APPS += ("subsites",)

THUMBNAIL_BACKGROUND = {
"class": "geonode.thumbs.background.GenericWMTSBackground",
    "options": {
        'url': "https://maps.info-rac.org/arcgis/rest/services/Hosted/basemap_inforac_3857/MapServer/WMTS",
        "layer": "Hosted_basemap_inforac_3857",
        "style": "default",
        "tilematrixset": "default028mm",
        "minscaledenominator": 272989.38673236995
    }
}

INSTALLED_APPS += ('rndt',)
LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"
CATALOG_METADATA_TEMPLATE = 'xml/template-rndt.xml'
CATALOG_METADATA_XSL = '/static/rndt/rndt-metadata.xsl'
ENABLE_CATALOG_HOME_REDIRECTS_TO = True

FACET_PROVIDERS = [
    {"class": "geonode.facets.providers.baseinfo.ResourceTypeFacetProvider"},
    {"class": "geonode.facets.providers.baseinfo.FeaturedFacetProvider"},
    {"class": "geonode.facets.providers.category.CategoryFacetProvider", "config": {"order": 5}},
    {"class": "geonode.facets.providers.keyword.KeywordFacetProvider", "config": {"order": 6}},
    {"class": "geonode.facets.providers.region.RegionFacetProvider", "config": {"order": 7}},
    {"class": "geonode.facets.providers.users.OwnerFacetProvider", "config": {"order": 8}},
    {"class": "geonode.facets.providers.thesaurus.ThesaurusFacetProvider"},
]

INSTALLED_APPS += ('infomapnode.fulltextsearch',)
GEONODE_APPS += ("infomapnode.fulltextsearch",)

