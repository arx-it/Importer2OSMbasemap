# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Importer2OSMbasemap
                                 A QGIS plugin
 Gestion de Plans 
                             -------------------
        begin                : 2015-08-25
        copyright            : (C) 2015 by arx iT
        email                : mba@arxit.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
from __future__ import absolute_import


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load Importer2OSMbasemap class from file Importer2OSMbasemap.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .main import Importer2OSMbasemap
    return Importer2OSMbasemap(iface)
