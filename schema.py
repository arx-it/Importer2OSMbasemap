'''
Created on 17 sept. 2022

@author: arxit
'''
from __future__ import absolute_import

from builtins import object
import os.path
import xml.etree.ElementTree as ET
from qgis.PyQt.QtCore import QFile, QIODevice, QVariant
from qgis.core import *

from . import main

class GeometryType(object):
    '''
    Geometry types
    '''

    POINT='POINT'
    POLYLINE='LINESTRING'
    POLYGON='POLYGON'

class DataType(object):
    '''
    Data types
    '''

    STRING='string'
    INTEGER='integer'
    DOUBLE='double'
    DATE='date'

XSD_GEOMETRY_TYPES = {'LUREF':GeometryType.POINT,
                      'gml:CurvePropertyType':GeometryType.POLYLINE,
                      'gml:SurfacePropertyType':GeometryType.POLYGON}

XSD_QGIS_DATATYPE_MAP = {DataType.STRING:QVariant.String,
                         DataType.INTEGER:QVariant.LongLong,
                         DataType.DOUBLE:QVariant.Double,
                         DataType.DATE:QVariant.String}

XSD_QGIS_GEOMETRYTYPE_MAP = {GeometryType.POINT:QgsWkbTypes.Point,
                             GeometryType.POLYLINE:QgsWkbTypes.LineString,
                             GeometryType.POLYGON:QgsWkbTypes.Polygon}

class PluginType(object):
    '''
    A plugin XSD type
    '''

    def __init__(self):
        '''
        Constructor
        '''

        self.geometry_type = None
        self.fields = list()

    def parse(self, name, xml_element, ns):
        '''
        Parse XML node

        :param name: The name of the type
        :type name: str, QString

        :param xml_element: The root XML node of the type (xsd:complexType)
        :type xml_element: Element

        :param ns: XSD namespaces
        :type ns: dict
        '''

        # Type name
        self.name = name
        self.geometry_type = None
        self.geometry_fieldname = None

        self.fields = list()
        self.ordered_field_names = list()

        sequence = xml_element.find('.//xsd:sequence',ns)
        elements = sequence.findall('xsd:element',ns)

        for element in elements:
            # Process geometry
            element_type = element.get('type')
            if element_type in XSD_GEOMETRY_TYPES:
                self.geometry_type = XSD_GEOMETRY_TYPES[element_type]
                self.geometry_fieldname = element.get('name')

            # Process field
            else:
                plugin_Field = PluginField()
                plugin_Field.parse(element, ns)
                self.fields.append(plugin_Field)

            self.ordered_field_names.append(element.get('name'))

    def friendlyName(self):
        '''
        Gets the friendly name of the type aka table name
        E.g. BIOTOPE_LIGNE for ARTIKEL17.BIOTOPE_LIGNE
        '''

        if self.name is None:
            return ''

        split = self.name.split('.')

        return split[-1]

    def topic(self):
        '''
        Gets the topic of the type
        E.g. ARTIKEL17 for ARTIKEL17.BIOTOPE_LIGNE
        '''

        if self.name is None:
            return ''

        split = self.name.split('.')

        return split[0]

    def getField(self, fieldname):
        '''
        Get a field from the name

        :param fieldname: The field name (ex : CODE)
        :type fieldname: str, QString
        '''

        for field in self.fields:
            if field.name == fieldname:
                return field

        return None

class PluginField(object):
    '''
    A plugin XSD field
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.nullable = True
        self.type = DataType.STRING
        self.length = None
        self.minvalue = None
        self.maxvalue = None
        self.listofvalues = None

    def parse(self, xml_element, ns):
        '''
        Parse XML node

        :param xml_element: The root XML node of the field (xsd:element)
        :type xml_element: Element

        :param ns: XSD namespaces
        :type ns: dict
        '''

        # Field name
        self.name = xml_element.get('name')

        # Field is nullable
        self.nullable = xml_element.get('minOccurs') is not None and xml_element.get('minOccurs')=='0'

        type = self._getDataType(xml_element, ns)

        # Data type
        self.type = type[0]

        # Text length
        self.length = type[1]

        # Numeric or date min value
        self.minvalue = type[2]

        # Numeric or date max value
        self.maxvalue = type[3]

        # List of possible values, enumeration
        self.listofvalues = type[4]

    def _getDataType(self, xml_element, ns):
        '''
        Returns the datatype of the field

        :param xml_element: The root XML node of the data type (xsd:element)
        :type xml_element: Element

        :param ns: XSD namespaces
        :type ns: dict
        '''

        # Dictionary of data types
        datatypes = {'xsd:string':DataType.STRING,
                     'xsd:normalizedString':DataType.STRING,
                     'xsd:integer':DataType.INTEGER,
                     'xsd:double':DataType.DOUBLE,
                     'xsd:decimal':DataType.DOUBLE,
                     'xsd:date':DataType.DATE}

        # XSD restriction element
        restriction = xml_element.find('.//xsd:restriction',ns)

        # Data type
        type = datatypes[restriction.get('base')]

        # Length
        length_element = restriction.find('xsd:maxLength',ns)
        length = length_element.get('value') if length_element is not None else None

        # Minimum inclusive value
        minvalue_element = restriction.find('xsd:minInclusive',ns)
        minvalue = minvalue_element.get('value') if minvalue_element is not None else None

        # Maximum inclusive value
        maxvalue_element = restriction.find('xsd:maxInclusive',ns)
        maxvalue = maxvalue_element.get('value') if maxvalue_element is not None else None

        # Enumeration
        enumeration_elements = restriction.findall('xsd:enumeration',ns)
        enumeration = list()
        for enumeration_element in enumeration_elements:
            enumeration.append(enumeration_element.get('value'))

        return type, length, minvalue, maxvalue, enumeration if len(enumeration)>0 else None

    def getEnumerationMap(self):
        map = dict()

        for element in self.listofvalues:
            map[element]=element

        return map