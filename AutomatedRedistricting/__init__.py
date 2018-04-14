# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutomatedRedistricting
                                 A QGIS plugin
 Creates electoral districts by algorithm
                             -------------------
        begin                : 2017-03-04
        copyright            : (C) 2017 by Andras Reka
        email                : andrasreka96@gmail.com
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
    """Load AutomatedRedistricting class from file AutomatedRedistricting.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .automated_redistricting import AutomatedRedistricting
    return AutomatedRedistricting(iface)
