'''
Created on 11 dec. 2015

@author: arxit
'''

from builtins import object
import os

from qgis.core import *
import qgis.utils
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtCore import QCoreApplication
import Importer2OSMbasemap.main

class TopoClean(object):
    '''
    Main class for the snapping widget
    '''

    def __init__(self, action):
        '''
        Constructor
        '''
        self.topoclean_action=action

    def run(self):
        '''
        Runs the widget
        '''

        project = Importer2OSMbasemap.main.current_project

        if not project.isImport2OSMProject():
            return

        self.topoclean_action.trigger()

        # Zoom to selected onclick button
        modification_Import2OSM_layer=project.getModificationImport2OSMLayer()

        if modification_Import2OSM_layer is not None:
            # Map layers in the TOC
            maplayers = QgsProject.instance().mapLayers()

            # Selection by intersection with 'MODIFICATION Import2OSM' layer
            for k,layer in list(maplayers.items()):
                if layer.type() != QgsMapLayer.VectorLayer or not Importer2OSMbasemap.main.current_project.isImport2OSMLayer(layer):
                    continue

                areas = []
                for Import2OSM_feature in modification_Import2OSM_layer.selectedFeatures():
                    cands = layer.getFeatures()
                    for layer_features in cands:
                        if Import2OSM_feature.geometry().intersects(layer_features.geometry()):
                            areas.append(layer_features.id())

                layer.select(areas)

            entity_count = modification_Import2OSM_layer.selectedFeatureCount()
            canvas = qgis.utils.iface.mapCanvas()
            canvas.zoomToSelected(modification_Import2OSM_layer)
            if entity_count==1:

                Importer2OSMbasemap.main.qgis_interface.messageBar().clearWidgets()
                Importer2OSMbasemap.main.qgis_interface.messageBar().pushMessage(QCoreApplication.translate('TopoClean','Information'),
                                                                   QCoreApplication.translate('TopoClean','There is 1 selected entity in MODIFICATION Import2OSM layer. You can now check geometries'))
            elif entity_count==0:
                Importer2OSMbasemap.main.qgis_interface.messageBar().pushMessage(QCoreApplication.translate('TopoClean','Information'),
                                                                   QCoreApplication.translate('TopoClean','There is no selected entity in MODIFICATION Import2OSM layer. You can now check geometries'))
            else:
                qgis.utils.iface.messageBar().pushMessage(QCoreApplication.translate('TopoClean', 'Information'),
                                                                   QCoreApplication.translate('TopoClean','There are {} selected entities in MODIFICATION Import2OSM layer. You can now check geometries').format(entity_count))
        else :
            qgis.utils.iface.messageBar().pushMessage("Error", "MODIFICATION Import2OSM layer is not correct")