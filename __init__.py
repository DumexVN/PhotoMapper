# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PhotoMapper
                                 A QGIS plugin
 Mapping Geotagged Photos
                             -------------------
        begin                : 2014-12-09
        copyright            : (C) 2014 by N/A
        email                : affirmativevn@gmail.com
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PhotoMapper class from file PhotoMapper.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .PhotoMapper import PhotoMapper
    return PhotoMapper(iface)
