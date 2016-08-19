# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PhotoMapperDialog
                                 A QGIS plugin
 Mapping Geotagged Photos
                             -------------------
        begin                : 2014-12-09
        git sha              : $Format:%H$
        copyright            : (C) 2014 by N/A
        email                : affirmativevn@gmail.com
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

from PyQt4 import QtGui, uic, QtCore

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'PhotoMapper_dialog_base.ui'))

# ADOPTED FROM PointConnecter Package
class PhotoMapperDialog(QtGui.QDialog, FORM_CLASS):
     def __init__(self, parent=None):
        #Constructor
        super(PhotoMapperDialog, self).__init__(parent)
        self.settings = QtCore.QSettings("whatsthis", "PhotoMapper")
        self.setupUi(self)
        self.browseVertexFileButton.clicked.connect(self.browseVertexFileButton_clicked)
        self.browseEdgeFileButton.clicked.connect(self.browseEdgeFileButton_clicked)
        self.browseGridFileButton.clicked.connect(self.browseGridFileButton_clicked)

     # ADOPTED FROM PointConnecter Package
     def browseVertexFileButton_clicked(self):
         lastShapeDir = self.settings.value("lastShapeDir", ".")
         pointFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', lastShapeDir, 'Vertex Files(*.txt *.csv)')
         self.vertexPathFileLineEdit.setText(pointFileName)
         (vertexDir, vertexFile) = os.path.split(pointFileName)
         self.settings.setValue("Vertex Directory", vertexDir)

     def browseEdgeFileButton_clicked(self):
         edgeDir = self.settings.value("lastShapeDir", ".")
         edgeFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', edgeDir, 'Vertex Files(*.txt *.csv)')
         self.edgePathFileLineEdit.setText(edgeFileName)
         (edgeDir, edgeFile) = os.path.split(edgeFileName)
         self.settings.setValue("Edge Directory",edgeDir)

     def browseGridFileButton_clicked(self):
         gridDir = self.settings.value("lastShapeDir", ".")
         gridFileName = QtGui.QFileDialog.getOpenFileName(self, 'Open File', gridDir, 'Grid Files(*.txt *.csv)')
         self.gridPathFileLineEdit.setText(gridFileName)
         (gridDir, gridFile) = os.path.split(gridFileName)
         self.settings.setValue("Grid Directory",gridDir)


# ADOPTED FROM PointConnecter Package


