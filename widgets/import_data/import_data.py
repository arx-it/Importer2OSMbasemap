'''
Created on 22 oct. 2022

@author: arxit
'''
from __future__ import absolute_import

from builtins import object
import os

from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox
from qgis.PyQt.QtCore import *

from ... import main

from .import_shp import ImportSHP
from .import_geojson import ImportGeoJSON
from .import_dxf import ImportDXF

class ImportData(object):
    '''
    Main class for the import data widget
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def run(self):
        '''
        Runs the widget
        '''

        if not main.current_project.isImport2OSMProject():
            return
        elif all(not isinstance(layer.layer(), QgsVectorLayer) for layer in QgsProject.instance().layerTreeRoot().findLayers()):
            QMessageBox.critical(None, 'Erreur', QCoreApplication.translate('ImportData','No layer imported'))
            return

        # Select file to import
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setOption(QFileDialog.ReadOnly)
        dialog.setNameFilter('Vector file (*.shp *.geojson *.dxf)');
        dialog.setWindowTitle(QCoreApplication.translate('ImportData','Select the file to import'))
        dialog.setSizeGripEnabled(False)
        result = dialog.exec_()

        if result == 0:
            return

        selected_file = dialog.selectedFiles()

        if len(selected_file)==0:
            return

        # Dispatch to the right importer
        importers = {
                    'shp':ImportSHP,
                    'geojson': ImportGeoJSON,
                    'dxf':ImportDXF
                    }

        extension = os.path.splitext(selected_file[0])[1][1:]
        self.importer = importers[extension](selected_file[0])
        self.importer.runImport()