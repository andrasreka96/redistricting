# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutomatedRedistricting
                                 A QGIS plugin
 Creates electoral districts by algorithm
                              -------------------
        begin                : 2017-03-04
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Andras Reka
        email                : andrasreka96@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon,QColor
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from automated_redistricting_dialog import AutomatedRedistrictingDialog
import os.path
import sys

from qgis.gui import QgsHighlight
from qgis.core import QgsExpression
from qgis.core import QgsMapLayerRegistry

from layer_manipulation.layer import LayerManipulation
from mosa.algorithm import MOSA
from util.util import Log
from logging.config import fileConfig
import logging


class AutomatedRedistricting:
    """QGIS Plugin Implementation."""

    ATTRIBUTE_NAME='name'
    ATTRIBUTE_POPULATION='pop2015'
    ATTRIBUTE_ID='natcode'
    ATTRIBUTE_NEIGHBOURS='neighbours'

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS    interface
        self.iface = iface


        # The plugin uses three different layers
        for layer in QgsMapLayerRegistry.instance().mapLayers().values():
            if (layer.name().find("poliline")!=-1):
                self.layer_poliline=layer
            if (layer.name().find("uat")!=-1):
                self.layer_poligon=layer


        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        #config logs
        logging_file = self.plugin_dir + "/logging_config.ini"
        fileConfig(logging_file)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'AutomatedRedistricting_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Automated Redistricting')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AutomatedRedistricting')
        self.toolbar.setObjectName(u'AutomatedRedistricting')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('AutomatedRedistricting', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = AutomatedRedistrictingDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/AutomatedRedistricting/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Automated Redistricting'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Automated Redistricting'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar



    def run(self):
        "Run method that performs all the real work"""
        mosa = MOSA(self.layer_poligon,self.layer_poliline)
        #log = Log()
        #lm = LayerManipulation(self.layer_poligon)

        #solution = mosa.CreateInitialSolution()
        #log.LogSolution(solution)
        #lm.ColorDistricts(solution.counties,'color')
        #solution2 = mosa.NeighbourSolution(solution)
        #log.LogSolution(solution2)
        #lm.ColorDistricts(solution2.counties,'color2')
        mosa.Anneal()
