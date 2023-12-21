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

from django.views.generic import TemplateView
from django.conf.urls import url, include
from geonode.urls import urlpatterns

urlpatterns += [
    url(r'^policy/', TemplateView.as_view(template_name='policy.html')),
    url(r'^guideline/', TemplateView.as_view(template_name='guideline.html')),
    # these paths hinders with subsite path configuration
    #url(r'^maps/', TemplateView.as_view(template_name='kmap/maps.html')),
    #url(r'^dashboards/', TemplateView.as_view(template_name='kmap/dashboards.html')),
    #url(r'^geostories/', TemplateView.as_view(template_name='kmap/geostories.html')),
    #url(r'^library/', TemplateView.as_view(template_name='kmap/library.html')),
    #url(r'^network/', TemplateView.as_view(template_name='kmap/network.html')),
    url(r"", include("subsites.urls")),
]
