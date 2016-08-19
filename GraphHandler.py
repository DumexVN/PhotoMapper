"""
/***************************************************************************
 PhotoMapper
                                 A QGIS plugin
            HANDLING ALL GRAPHS RELATED FUNCTIONS
            BUILT ON PlUG-INS OF POINTS2ONE; POINTSTOPATH; POINTSCONNECTOR
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
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

import qgis.utils
import math
import codecs
import os
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'GraphHandler_ui.ui'))

class GraphHandler(QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(GraphHandler, self).__init__(parent)
        self.setupUi(self)
        self.bar = QgsMessageBar()
        self.v_list = []
        self.e_list = []
    #VALIDATE FILES PATH

    #GENERATE VERTEX LIST FROM THE FILE
    #AND CREATE THE VERTEX LAYER
    def generate_graph(self, vertexPath, edgePath):
        uri = "file:///" + vertexPath + "?type=csv&delimiter=;&xField=long&yField=lat&spatialIndex=no&subsetIndex=no&watchFile=no"
        #process the layer, extracting each vertex to create new_ui vertex list:
        vertex_layer = QgsVectorLayer(uri, 'vertex', 'delimitedtext')
        if not vertex_layer.isValid():
            QMessageBox.information(None, "Error", "File Not Valid")
            return
        vertex_iter = vertex_layer.getFeatures()
        vertex_list = {}

        #BUIDLING VERTEX LIST
        progressMessageBar = self.bar.createMessage("Building point database...")
        progress = QProgressBar()
        progress.setMaximum(vertex_layer.featureCount())
        progress.setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        progressMessageBar.layout().addWidget(progress)
        self.bar.pushWidget(progressMessageBar, self.bar.INFO)
        for vertex in vertex_iter:
            geom = vertex.geometry()
            if not geom.type() == QGis.Point: #CHECK IF IT'S A VERTEX
                QMessageBox.information(None, "Error", "Invalid Vertex at:" + vertex.id())
                return
            i = geom.asPoint()
            indx = str(vertex.attribute('id'))
            vertex_list[indx] = i

        #adding Layer to MapLayerRegistry:
        vertex_layer_symbols = vertex_layer.rendererV2().symbols()
        v_symbol = vertex_layer_symbols[0]
        v_symbol.setSize(1.5)
        v_symbol.setColor(QColor.fromRgb(102, 244, 251))
        QgsMapLayerRegistry.instance().addMapLayer(vertex_layer)
        self.bar.clearWidgets()
        #creating edge list from file:
        edge_list = []
        if (not edgePath):
            QMessageBox.information(None, "Error", "Missing Edge Path")
        else:
            p = open(edgePath, 'r')
            for line in p:
                line = line.splitlines()
                for s in line:
                    s = tuple(s.split(','))
                    edge_list.append(s)
            p.close()
            #Preprocessing edge layer:
            edge_layer = QgsVectorLayer('LineString?crs='+vertex_layer.crs().authid(),
                                            'lines', 'memory')
            edge_layer.startEditing()
            edge_data_provider = edge_layer.dataProvider()
            edge_data_provider.addAttributes ([ QgsField('from', QVariant.Int), QgsField('to', QVariant.Int)] )
            #PROGRESS BAR
            count = 0
            for edge in edge_list:
                try:
                        fromVertex = vertex_list[str(edge[0])]
                        toVertex = vertex_list[str(edge[1])]
                except IndexError:
                    QMessageBox.information(None, "Error", "Index Out Of Bounds!")
                    return
                if fromVertex == toVertex:
                    pass
                else:
                    new_edge = QgsGeometry.fromPolyline([fromVertex, toVertex])
                    feat = QgsFeature()
                    feat.setGeometry(new_edge)
                    feat.setAttributes([ str(edge[0]) , str(edge[1]) ])
                    (res, outFeats) = edge_data_provider.addFeatures([feat])
                    edge_layer.commitChanges()
                    if res != True:
                            pass
                    count += 1
            edge_symbols = edge_layer.rendererV2().symbols()
            edge_symbol = edge_symbols[0]
            edge_symbol.setColor(QColor(0,0,0))
            edge_symbol.setWidth(0.1)
            QgsMapLayerRegistry.instance().addMapLayer(edge_layer)
        self.v_list = vertex_list #SAVING VERTEX AND EDGE FOR LATER CALCULATION
        self.e_list = edge_list

    #READ IN FILES AND GETTING INFO
    def generate_grid(self, gridPath):
        p = open(gridPath, 'r')
        lines = p.read().splitlines()
        upleft_coor = map(float, lines[0].split(','))
        downright_coor = map(float, lines[1].split(','))
        cell_size = float(lines[2])
        #GRID WITH SIZE x*y
        y = lines.__len__() - 3
        x = lines[3].split(',').__len__()
        #CREATING THE GRID
        grid =[[0 for i in range (0,x)] for i in range (0,y)]
        mySum = 0.0
        _myMax  = 0.0
        #VISUALISE THE GRID USING A MATRIX
        for i in range (3, lines.__len__()):
            line = lines[i].replace(',',' ')
            value = line.split(' ')
            for g in value:
                try:
                    mySum += int(g)
                    if (int(g) > _myMax):
                        _myMax = float(g)
                except ValueError:
                    pass
            grid[i-3] = line #COPY MATRIX FOR TRANSPARENCY
        #VISUALISE THE GRID DEPENDS ON THE MATRIX
        poly_layer = QgsVectorLayer("polygon?crs=epsg:4326&field=",
                                        'My Grids', 'memory')
        poly_layer.startEditing()
        poly_data_provider = poly_layer.dataProvider()

        poly_data_provider.addAttributes ([ QgsField('density', QVariant.Int), QgsField('tags', QVariant.String)] )
        #ADDING tags ENTRY
        tag_array =[['' for i in range (0,x)] for i in range (0,y)]
        msgbox = QMessageBox()
        msgbox.setText('Select tags file ?')
        msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        ret = msgbox.exec_()
        if ret == QMessageBox.Ok:
            tagsFilePath =  QFileDialog.getOpenFileName(self, None, "Select GRIDFILE Path")
            if not os.path.isfile(tagsFilePath):
                qWarning("ERROR FILE MISSED, SKIPPING")
            else:
                f = open(tagsFilePath, 'r')
                flines = f.read().splitlines()
                y2 = flines.__len__()
                x2 = flines[3].split(';').__len__()
                for i in range (0, y2-1):
                    line = flines[i].replace(',',' ')
                    tags = line.split(';')
                    for n in range (0, x2-1):
                        tag = tags[n]
                        tag_array[i][n] = tag
        else:
            pass
        #BUILDING THE GRID, ADDING LAYERS AND ATTRIBUTES
        for i in range (0, y):
            uplat = upleft_coor[0]-(cell_size*i)
            uplong = upleft_coor[1]
            density_vec = grid[i].split()
            for n in range (1, x):
                #BOUNDING RECT
                upleftPoint = QgsPoint(uplong + (cell_size*(n-1)), uplat)
                uprightPoint = QgsPoint(uplong + (cell_size*n), uplat)
                downleftPoint = QgsPoint(uplong + (cell_size*(n-1)), uplat - cell_size)
                downrightPoint = QgsPoint(uplong + (cell_size*n), uplat - cell_size)
                new_poly = QgsGeometry.fromPolygon([[upleftPoint, uprightPoint, downrightPoint, downleftPoint]])
                feat = QgsFeature()
                feat.setGeometry(new_poly)
                density = density_vec[n-1]
                tags = tag_array[i][n-1]
                feat.setAttributes([ str(density), tags ])
                (res, outFeats) = poly_data_provider.addFeatures([feat])
                poly_layer.commitChanges()
                if res != True:
                        pass

        #CREATING CUSTOMISED RENDERER LAYER
        #GENERATING SYMBOLS LAYER
        myTargetField = 'density'
        myRangeList = []
        myOpacity = 0.70
        #COLOUR RAMP HARDCODE
        myColourRamp = QgsVectorGradientColorRampV2()
        myColourRamp.setColor2(QColor.fromRgb(8,48,107))
        myColourRamp.setColor1(QColor.fromRgb(255,255,255))
        #CREATING SYMBOLS AND RANGE EQUAL INTERVAL
        poly_layer.rendererV2()
        """
        #CALLING A INPUT DIALOG
        classes = 0
        val, ok = QInputDialog.getInt(self, 'Numbers of Interval','Enter a int: ', 0, 0, 100, 1)
        if ok:
            classes = val
        """

        #MANUALLY ADDING 5 CLASSES
        myMin = 0
        myMax = 0
        for i in range (1, 6):
            if (i == 1):
                pass
            elif (i == 2):
                myMin = myMax + 1
                myMax = 10
            elif (i == 3):
                myMin = myMax + 1
                myMax = 50
            elif (i == 4):
                myMin = myMax + 1
                myMax = 500
            elif (i == 5):
                myMin = myMax + 1
                myMax = _myMax
            myLabel = str(myMin) + '-' + str(myMax)
            mySymbol = QgsSymbolV2.defaultSymbol(poly_layer.geometryType())
            mySymbol.setAlpha(myOpacity)
            myRange = QgsRendererRangeV2(myMin, myMax, mySymbol, myLabel)
            myRangeList.append(myRange)
        ##################################################################
        #FINALISE
        myRenderer = QgsGraduatedSymbolRendererV2('Clusters', myRangeList)
        myRenderer.updateColorRamp(myColourRamp)
        myRenderer.setClassAttribute(myTargetField)
        myRenderer.setMode(QgsGraduatedSymbolRendererV2.EqualInterval)
    #    myRenderer.updateClasses(poly_layer,QgsGraduatedSymbolRendererV2.Quantile, classes)
        poly_layer.setRendererV2(myRenderer)
        QgsMapLayerRegistry.instance().addMapLayer(poly_layer)

    def checksize(self):
        size = "Vertices:"
        size += str(self.v_list.__len__()-1)
        size += "; Edges: "+ str(self.e_list.__len__())
        return size