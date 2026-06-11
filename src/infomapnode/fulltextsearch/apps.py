#########################################################################
#
# Copyright (C) 2023 OSGeo
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
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class FullTextSearchConfig(AppConfig):
    name = "infomapnode.fulltextsearch"
    verbose_name = "Full Text Search"

    def ready(self):
        super().ready()

        from geonode.base.api.views import ResourceBaseViewSet
        from geonode.base.api.filters import DynamicSearchFilter
        from infomapnode.fulltextsearch.filters import FTSDynamicSearchFilter

        for i in range(len(ResourceBaseViewSet.filter_backends)):
            if ResourceBaseViewSet.filter_backends[i] == DynamicSearchFilter:
                logger.warning("Replacing DynamicSearchFilter")
                ResourceBaseViewSet.filter_backends[i] = FTSDynamicSearchFilter

