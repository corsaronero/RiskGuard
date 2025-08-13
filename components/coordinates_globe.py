from qgis.PyQt import QtWidgets
from qgis.core import QgsProject, QgsRasterLayer, QgsRectangle, QgsPointXY, QgsWkbTypes, QgsCoordinateTransform, QgsCoordinateReferenceSystem
from qgis.gui import QgsMapCanvas, QgsMapToolEmitPoint, QgsRubberBand, QgsMapToolPan
from PyQt5.QtCore import Qt, pyqtSignal

class GlobeMapForm(QtWidgets.QWidget):
    # Create a signal to send the coordinates
    coordinates_saved = pyqtSignal(float, float, float, float)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the form layout and map canvas
        self.layout = QtWidgets.QVBoxLayout()
        self.layer = None  # Store a reference to the OpenStreetMap layer

        # Initialize the map canvas (2D)
        self.map_canvas = QgsMapCanvas()
        self.map_canvas.setCanvasColor(Qt.white)
        
        # Set up the OpenStreetMap layer
        self.setup_map()

        # Add the map canvas to the layout
        self.layout.addWidget(self.map_canvas)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Add zoom buttons
        self.add_zoom_buttons()

        # Add a "Draw Rectangle" button and Save
        button_map_layout = QtWidgets.QHBoxLayout()
        self.draw_rectangle_button = QtWidgets.QPushButton("Draw Rectangle")
        self.save_coordinates_button = QtWidgets.QPushButton("Save")

        self.draw_rectangle_button.clicked.connect(self.enable_rectangle_drawing)
        self.save_coordinates_button.clicked.connect(self.save_coordinates)

        button_map_layout.addWidget(self.draw_rectangle_button)  # Add the button below the map canvas
        button_map_layout.addWidget(self.save_coordinates_button)
        self.layout.addLayout(button_map_layout)

        self.setLayout(self.layout)

        # Set window properties for the form
        self.setWindowTitle("2D Earth Map Viewer with Rectangle Drawing")
        #self.setGeometry(100, 100, 800, 600)

        self.resize(570, 600)  # Set the window size
        #canvas_size = self.map_canvas.size()
        #self.resize(canvas_size.width(), canvas_size.height())

        # Center the form over the parent window
        if parent is not None:
            self.move_to_center(parent)

        # Set the window as a modal window (optional)
        self.setWindowModality(Qt.WindowModal)

        # Initialize the tool to draw a rectangle
        self.rubber_band = QgsRubberBand(self.map_canvas, QgsWkbTypes.PolygonGeometry)
        self.rubber_band.setStrokeColor(Qt.red)
        self.rubber_band.setWidth(2)
        
        # Set up map tool to detect mouse clicks
        self.map_tool_rectangle  = QgsMapToolEmitPoint(self.map_canvas)
        self.map_tool_rectangle.canvasClicked.connect(self.on_map_clicked)

        self.map_tool_pan = QgsMapToolPan(self.map_canvas)  # Pan tool

        # Set panning as the default tool
        self.map_canvas.setMapTool(self.map_tool_pan)  # Enable panning by default
        
        # Variables to hold rectangle coordinates
        self.start_point = None
        self.end_point = None

    def move_to_center(self, parent):
        """Center the window over the parent."""
        parent_geom = parent.frameGeometry()
        center_point = parent_geom.center()
        self.move(center_point.x() - self.width() // 2, center_point.y() - self.height() // 2)

    def setup_map(self):
        """Set up the 2D map with an OpenStreetMap base layer."""
        # Create an OpenStreetMap layer (or any other XYZ tile layer)
        url = "type=xyz&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png"
        self.layer = QgsRasterLayer(url, "OpenStreetMap", "wms")

        # Check if the layer is valid
        if not self.layer.isValid():
            print("Failed to load the OpenStreetMap layer!")
            return
        
        # Add the layer to the QGIS project
        #QgsProject.instance().addMapLayer(self.layer)

        # Set the canvas to display the layer
        self.map_canvas.setLayers([self.layer])
        self.map_canvas.setExtent(self.layer.extent())
        self.map_canvas.refresh()

        # Ensure the map canvas resizes dynamically with the panel
        self.map_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


    def add_zoom_buttons(self):
        """Create zoom in and zoom out buttons and add them to the layout."""
        button_layout = QtWidgets.QHBoxLayout()

        # Create zoom in (+) button
        self.zoom_in_button = QtWidgets.QPushButton("+")
        self.zoom_in_button.clicked.connect(self.zoom_in)

        # Create zoom out (-) button
        self.zoom_out_button = QtWidgets.QPushButton("-")
        self.zoom_out_button.clicked.connect(self.zoom_out)

        # Add buttons to the horizontal layout
        button_layout.addWidget(self.zoom_in_button)
        button_layout.addWidget(self.zoom_out_button)

        # Add the button layout to the main layout (below the map)
        self.layout.addLayout(button_layout)

    def zoom_in(self):
        """Zoom in on the map canvas."""
        current_scale = self.map_canvas.scale()
        self.map_canvas.zoomScale(current_scale * 0.8)  # Zoom in by decreasing scale

    def zoom_out(self):
        """Zoom out on the map canvas."""
        current_scale = self.map_canvas.scale()
        self.map_canvas.zoomScale(current_scale / 0.8)  # Zoom out by increasing scale


    def enable_rectangle_drawing(self):
        """Activate the rectangle drawing tool."""
        self.map_canvas.setMapTool(self.map_tool_rectangle)
        print("Rectangle drawing tool enabled. Click on the map to start drawing.")

    def on_map_clicked(self, point: QgsPointXY):
        """Handle map clicks to start and end the rectangle drawing."""
        if self.start_point is None:
            # First click: Start the rectangle
            self.start_point = point
            print(f"Start point: {self.start_point}")
        else:
            # Second click: End the rectangle and draw it
            self.end_point = point
            print(f"End point: {self.end_point}")
            self.draw_rectangle()
            self.start_point = None  # Reset for the next rectangle
            # Switch back to panning mode after drawing the rectangle
            self.map_canvas.setMapTool(self.map_tool_pan)

    def draw_rectangle(self):
        """Draw the rectangle using QgsRubberBand and return coordinates."""
        if self.start_point and self.end_point:
            # Create a rectangle from the two points
            rect = QgsRectangle(self.start_point, self.end_point)

            # Clear any previous rubber bands
            self.rubber_band.reset(QgsWkbTypes.PolygonGeometry)

            # Add points to the rubber band to draw the rectangle
        self.rubber_band.addPoint(QgsPointXY(rect.xMinimum(), rect.yMinimum()))
        self.rubber_band.addPoint(QgsPointXY(rect.xMinimum(), rect.yMaximum()))
        self.rubber_band.addPoint(QgsPointXY(rect.xMaximum(), rect.yMaximum()))
        self.rubber_band.addPoint(QgsPointXY(rect.xMaximum(), rect.yMinimum()))
        self.rubber_band.addPoint(QgsPointXY(rect.xMinimum(), rect.yMinimum()))  # Close the polygon

        self.rubber_band.show()

        # Create a coordinate transform to convert from layer's CRS to EPSG:4326 (WGS 84)
        src_crs = self.map_canvas.mapSettings().destinationCrs()  # Layer's CRS

        if not src_crs.isValid():
            print("Source CRS is invalid, setting fallback to EPSG:3857")
            src_crs = QgsCoordinateReferenceSystem(3857)  # EPSG:3857 (Web Mercator)

        #transform = QgsCoordinateTransform(layer_crs, QgsCoordinateReferenceSystem('EPSG:4326'), QgsProject.instance())
        dest_crs = QgsCoordinateReferenceSystem(4326)  # EPSG:4326 for lat/lon

        # Ensure the source CRS is set properly
        print(f"Source CRS: {src_crs.authid()}")  # Check if the source CRS is correct

        # Create a QgsCoordinateTransform object to handle the CRS transformation
        transform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())


        # Convert map coordinates to latitude and longitude
        min_point = transform.transform(QgsPointXY(rect.xMinimum(), rect.yMinimum()))
        max_point = transform.transform(QgsPointXY(rect.xMaximum(), rect.yMaximum()))


        min_lon, min_lat = min_point.x(), min_point.y()
        max_lon, max_lat = max_point.x(), max_point.y()


        # Calculate the north, south, east, and west boundaries
        self.north = max_lat
        self.south = min_lat
        self.east = max_lon
        self.west = min_lon

        # Debugging - print the source CRS and transformed coordinates
        print(f"Source CRS: {src_crs.authid()}")  # Ensure this matches your map projection
        print(f"Southwest Corner (Lat, Lon): ({self.south}, {self.west})")
        print(f"Northeast Corner (Lat, Lon): ({self.north}, {self.east})")

        # Update the UI with these values
        self.display_coordinates()

    # Define a method to update labels
    def display_coordinates(self):

        # If the grid layout doesn't exist yet, create it
        if not hasattr(self, 'coord_grid'):
            self.coord_grid = QtWidgets.QGridLayout()
            self.layout.addLayout(self.coord_grid)

        # Remove any previous widgets in the grid layout (clearing old data)
        while self.coord_grid.count():
            child = self.coord_grid.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.label_north = QtWidgets.QLabel(f"North: {self.north}")
        self.label_south = QtWidgets.QLabel(f"South: {self.south}")
        self.label_east = QtWidgets.QLabel(f"East: {self.east}")
        self.label_west = QtWidgets.QLabel(f"West: {self.west}")

        # Add the labels to the grid layout (2 columns)
        self.coord_grid.addWidget(self.label_north, 0, 0)  
        self.coord_grid.addWidget(self.label_south, 1, 0) 
        self.coord_grid.addWidget(self.label_east, 0, 1)  
        self.coord_grid.addWidget(self.label_west, 1, 1)  

        self.coord_grid.setContentsMargins(10, 10, 10, 10)  # Set margin around the grid
        self.coord_grid.setSpacing(5)  # Set spacing between labels

    def save_coordinates(self):
        """Emit the north, south, east, and west coordinates when saving."""
        if self.end_point:
            self.coordinates_saved.emit(self.north, self.west, self.south, self.east)
            # Close the GlobeMapForm after saving the coordinates
            self.close()
        else:
            print("Coordinates are not ready for emission.")

    def closeEvent(self, event):
        #print(f"Layer {self.layer.id()} removed from QGIS.")
        """Handle the window close event and remove the map layer from QGIS."""
        if self.layer:
            QgsProject.instance().removeMapLayer(self.layer.id())  # Remove the layer by ID
        else:
            print("Layer already deleted or not found.")
        
        event.accept()  # Accept the close event





