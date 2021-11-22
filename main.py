# -*- coding: utf-8 -*-
'''
/***************************************************************************
 Importer2OSM
                                 A QGIS plugin
 Gestion de Plans d'Aménagement Général du Grand-Duché de Luxembourg
                              -------------------
        begin                : 2015-08-25
        git sha              : $Format:%H$
        copyright            : (C) 2015 by arx iT
        email                : mba@arxit.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
'''
from __future__ import absolute_import
from builtins import object
from qgis.core import *
from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction, QPushButton
from qgis.PyQt.QtGui import QIcon
# Initialize Qt resources from file resources.py
from . import resources
# Import the code for the dialog
import os.path
# Widgets
from .widgets.create_project.create_project import *
from .widgets.import_data.import_data import *
from .widgets.import_manager.import_manager import *
#from .widgets.export_gml.export_gml import *
#from .widgets.stylize.stylize import *
#from .widgets.data_checker.data_checker import *
#from .widgets.topoclean.topoclean import *
#from .widgets.topology.topology import *
#from .widgets.about.about import *
#from .editor import simple_filename, precise_range
# Schema
from Importer2OSM.schema import *
from Importer2OSM.project import *

# Global variables
plugin_dir = os.path.dirname(__file__)
xsd_schema = OSMSchema()
qgis_interface = None
current_project = Project()

class Importer2OSM(object):
    '''
    QGIS Plugin Implementation.
    '''

    def __init__(self, iface):
        '''Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        '''

        # Save reference to the QGIS interface
        global qgis_interface
        qgis_interface = iface
        self.iface = iface

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            plugin_dir,
            'i18n',
            '{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Register custom editors widgets

        # Declare instance attributes
        self.actions = []
        self.pag_actions = [] #Importer2OSM actions, disabled if the project is not PAG
        self.menu = self.tr(u'&Importer2OSM')

        # Toolbar initialization
        self.toolbar = self.iface.addToolBar(u'Importer2OSM')
        self.toolbar.setObjectName(u'Importer2OSM')

        # QGIS interface hooks
        self.iface.projectRead.connect(current_project.open)
        self.iface.newProjectCreated.connect(current_project.open)
        current_project.ready.connect(self.updateGui)

        # Load current project
        current_project.open()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        '''Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        '''
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PAGLuxembourg', message)


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
        '''Add a toolbar icon to the toolbar.

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
        '''

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        if callback is not None:
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
        '''
        Create the menu entries and toolbar icons inside the QGIS GUI.
        '''

        # New project
        self.create_project_widget=CreateProject()
        self.add_action(
            ':/plugins/Importer2OSM/widgets/create_project/icon.png',
            text=self.tr(u'New project'),
            callback=self.create_project_widget.run,
            status_tip=self.tr(u'Creates a new PAG project'),
            parent=self.iface.mainWindow())

        # Import data
        self.import_data_widget = ImportData()
        self.pag_actions.append(self.add_action(
            ':/plugins/Importer2OSM/widgets/import_data/icon.png',
            text=self.tr(u'Import data'),
            callback=self.import_data_widget.run,
            status_tip=self.tr(u'Import data from files (GML, SHP, DXF)'),
            parent=self.iface.mainWindow()))

        # Import manager
        self.import_manager_widget = ImportManager()
        self.pag_actions.append(self.add_action(
            ':/plugins/Importer2OSM/widgets/import_manager/icon.png',
            text=self.tr(u'Import manager'),
            callback=self.import_manager_widget.run,
            status_tip=self.tr(u'Open the import manager'),
            parent=self.iface.mainWindow()))

        # Update buttons availability
        self.updateGui()

    def updateGui(self):
        '''
        Updates the plugin GUI
        Disable buttons
        '''
        enabled = current_project.isImport2OSMProject()
        #enabled = True

        for action in self.pag_actions:
                action.setEnabled(enabled)

    def _showMissingTopolPluginMessage(self):
        '''
        Display a message to prompt the user to install the topology checker plugin
        '''

        self._showMissingPluginMessage(u'Topology Checker')

    def _showMissingGeometryCheckerPluginMessage(self):
        '''
        Display a message to prompt the user to install the topology checker plugin
        '''

        self._showMissingPluginMessage(u'Geometry Checker')

    def _showMissingPluginMessage(self, plugin):
        '''
        Display a message to prompt the user to install the geometry checker plugin
        '''
        widget = self.iface.messageBar().createMessage(self.tr(u'PAG Luxembourg'), self.tr(u'The "') + plugin + self.tr(u'" plugin is required by the "PAG Luxembourg" plugin, please install it and restart QGIS.'))
        button = QPushButton(widget)
        button.setText(self.tr(u'Show plugin manager'),)
        button.pressed.connect(self.iface.actionManagePlugins().trigger)
        widget.layout().addWidget(button)
        self.iface.messageBar().pushWidget(widget, 2) #Critical = 2

    def unload(self):
        '''
        Removes the plugin menu item and icon from QGIS GUI.
        '''

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PAG Luxembourg'),
                action)
            self.iface.removeToolBarIcon(action)

        # remove the toolbar
        del self.toolbar

        # Disconnect Signals
        self.iface.projectRead.disconnect(current_project.open)
        self.iface.newProjectCreated.disconnect(current_project.open)
        current_project.ready.disconnect(self.updateGui)