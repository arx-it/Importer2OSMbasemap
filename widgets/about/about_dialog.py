# -*- coding: utf-8 -*-
"""
/***************************************************************************
 CreateProjectDialog
                                 A QGIS plugin

                             -------------------
        begin                : 2022-09-09
        git sha              : $Format:%H$
        copyright            : (C) 2022 by arx iT
        email                : pln@arxit.com
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

import os

from qgis.PyQt import QtGui, uic
from qgis.PyQt.QtWidgets import QDialog, QFileDialog, QMessageBox
from qgis.PyQt.QtGui import QPixmap, QDesktopServices
from qgis.PyQt.QtCore import QCoreApplication, QUrl

from ... import main

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'about_dialog.ui'))


class AboutDialog(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        '''
        Constructor.
        '''

        super(AboutDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        logo_path = os.path.join(
            main.plugin_dir,
            'widgets',
            'about',
            'logo_arxit.png')
        pixmap = QPixmap(logo_path)
        self.lblLogoArxit.setPixmap(pixmap)

    def _showHelp(self):
        help_path = os.path.join(
            main.plugin_dir,
            'help',
            'user',
            'index.html')
        QDesktopServices.openUrl(QUrl('file:///' + help_path, QUrl.TolerantMode))