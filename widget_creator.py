from qgis.PyQt import QtWidgets
from PyQt5 import QtCore
from .flow_layout import FlowLayout
from .components.accordion_component import Accordion
from .services.data_download import DownloadServices
from .services.data_services import DataServices
from .controller.update_constraints import UpdateConstraints
from .components.coordinates_globe import GlobeMapForm
from .module.display_error_message import DisplayErrorMessage
from .controller.accept_licences import AcceptLicences
import sip
from copy import deepcopy


class WidgetCreator:
    def __init__(self, dialog, layout):
        self.dialog = dialog
        self.verticalLayout = layout
        self.error_display = DisplayErrorMessage(self.verticalLayout, parent=self.dialog)
        self.group_boxes = [] 
        self.radio_button_group = QtWidgets.QButtonGroup(self.dialog)
        self.labelWidget = None 
        self.geographicExtentMap = None
        self.geographicLocationMap = None
        #self.selected_items = {}
        self.batch_update = False  # Flag to handle batch updates

        self.selected_data = {}  # Dictionary to hold selected data dynamically forCMCC
        
        # Initialize the widgets dictionary to store widget references for use constrains
        self.widgets_store = {}  
        self.url_data_constraints = None
        self.extent_inputs = {}  # Dictionary to store references to the QLineEdit fields n,w,s,e

        self.dynamic_widgets = []

        self.task = None

    def clear_dynamic_widgets(self):
        for widget in self.dynamic_widgets:
            if widget.parent() is not None:
                widget.setParent(None)
            widget.deleteLater()
        self.dynamic_widgets = []  # Reset the list
        
    def create_copernicus_widgets(self, dataset_json, url_constrain, dataset_selected, licences_list):
        self.clear_dynamic_widgets()

        self.geographicLocationMap = None
        self.url_data_constraints = url_constrain
        self.labelErrorNoInfo = None
        self.selected_items = {}
        self.source_name = 'CDS'
        self.update_handler = UpdateConstraints(self, self.url_data_constraints)
        self.dataset_selected = dataset_selected
        self.area_input = {}
        self.licence_labels = {}


        def create_widget(item, parent_layout, processed_widgets):
            # Skip if the widget has already been processed
            if item['name'] in processed_widgets:
                return
            
            # Mark this widget as processed
            processed_widgets.add(item['name'])

            groupBox = QtWidgets.QGroupBox(item['label'], self.dialog)
            groupBoxLayout = QtWidgets.QVBoxLayout()

            # Handle "required" attribute by adding a label for required fields
            validation_label = None
            if item.get('required', False):
                validation_label = QtWidgets.QLabel("This is a required parameter", groupBox)
                validation_label.setStyleSheet("color: red;")
                validation_label.setVisible(True) 
                groupBoxLayout.addWidget(validation_label)

                # Store validation label for later use
                if not hasattr(self, "validation_labels"):
                    self.validation_labels = {}
                self.validation_labels[item["name"]] = validation_label

                    
            # GeographicalArea If item name is 'global' or 'area', add a radio button
            if item['name'] in ['global', 'area']:
                radio_button = QtWidgets.QRadioButton(item['label'], self.dialog)
                groupBoxLayout.addWidget(radio_button)
                self.radio_button_group.addButton(radio_button)
                # Connect the radio button to the handler
                if item['name'] == 'global':
                    if not sip.isdeleted(radio_button):
                        radio_button.setChecked(True)
                        radio_button.toggled.connect(lambda checked:self.handle_global_area_radio_button(checked, 'global'))
                elif item['name'] == 'area':
                    radio_button.toggled.connect(lambda checked:self.handle_global_area_radio_button(checked, 'area'))
                    radio_button.toggled.connect(lambda checked, gb=item['name'], v=self.area_input, t='area':
                               self.create_selected_items(gb, v, QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked, t))
                    

                def delayed_initialization():
                    # Connect the radio button to the handler
                    self.handle_global_area_radio_button(True, 'global')

                # Set a timer to call the initialization function after a small delay (e.g., 100 ms)
                QtCore.QTimer.singleShot(500, delayed_initialization)

            groupBox.setLayout(groupBoxLayout)
            parent_layout.addWidget(groupBox)

            self.group_boxes.append(groupBox)

            flowLayout = FlowLayout()
            groupBoxLayout.addLayout(flowLayout)

            if "details" in item:
                widget_type = item['type']
                groupBoxName = item['name']  # Name of the group box, e.g., 'year'
                if groupBoxName not in self.widgets_store:
                    self.widgets_store[groupBoxName] = {}

                def update_validation_label(widgets_list):
                    """Hide or show the validation label based on selection state."""
                    if any(widget.isChecked() for widget in widgets_list):
                        if validation_label:
                            validation_label.setVisible(False)  # Hide the validation message
                    else:
                        if validation_label:
                            validation_label.setVisible(True)  # Show the validation message again


                if widget_type == 'StringListWidget':
                    labels = item.get('details', {}).get('labels', 'No labels found').values()
                    values = item.get('details', {}).get('values', [])
                    default = item.get('details', {}).get('default', [])

                    # Ensure 'default' is a list
                    if not isinstance(default, list):
                        default = [default]  # Convert to a list if it's not already a list

                    checkboxes = []
                    if labels != 'No labels found':
                        for idx, label in enumerate(labels):
                            checkLabel = QtWidgets.QCheckBox(label, groupBox)

                            value = values[idx]
                            if value in default:
                                checkLabel.setChecked(True)
                                # Manually call the update_constraints function if the checkbox is pre-checked
                                #self.update_handler.update_constraints(item['name'], value, 2, widget_type)  # state 2 means 'Checked'
                                QtCore.QTimer.singleShot(400, lambda val=value: self.create_selected_items(item['name'], val, 2, widget_type))

                                if validation_label:
                                    validation_label.setVisible(False)  # Hide validation if a default is already selected

                            #checkLabel.stateChanged.connect(lambda state, gb=item['name'], v=value, t=widget_type: self.update_handler.update_constraints(gb, v, state, t))
                            checkLabel.stateChanged.connect(lambda state, gb=item['name'], v=value, t=widget_type: self.create_selected_items(gb, v, state, t))
                            checkLabel.stateChanged.connect(lambda: update_validation_label(checkboxes))  # Connect to validation update

                            flowLayout.addWidget(checkLabel)
                            checkboxes.append(checkLabel)
                            self.widgets_store[groupBoxName][value] = checkLabel
                            #self.widgets_store[groupBoxName][label] = checkLabel

                        self.addButtonSelectCleanAll(groupBoxLayout, checkboxes, item['name'], widget_type, values, validation_label)

                elif widget_type == 'StringChoiceWidget':
                    labels = item.get('details', {}).get('labels', 'No labels found').values()
                    values = item.get('details', {}).get('values', [])
                    default = item.get('details', {}).get('default', [])

                    radio_buttons = []
                    if labels != 'No labels found':
                        for idx, label in enumerate(labels):
                            radioLabel = QtWidgets.QRadioButton(label, groupBox)
                            value = values[idx]
                            if value in default:
                                radioLabel.setChecked(True)
                                QtCore.QTimer.singleShot(400, lambda val=value: self.create_selected_items(item['name'], val, 2, widget_type))
                                #self.create_selected_items(item['name'], value, 2, widget_type)
                                if validation_label:
                                    validation_label.setVisible(False)

                            flowLayout.addWidget(radioLabel)
                            try:
                                radioLabel.toggled.disconnect()  # Disconnect all slots connected to 'toggled'
                            except TypeError:
                                pass
                            radioLabel.toggled.connect(lambda checked, gb=item['name'], v=value, t=widget_type: self.create_selected_items(gb, v, 2 if checked else 0, t))
                            radioLabel.toggled.connect(lambda: update_validation_label(radio_buttons))  # Connect to validation update
                            radio_buttons.append(radioLabel)
                            self.widgets_store[groupBoxName][value] = radioLabel
                            # Connect the signal to update constraints using the 'toggled' signal for radio buttons
                            #radioLabel.toggled.connect(lambda checked, gb=item['name'], cl=radioLabel.text(), t=widget_type: self.update_handler.handle_radio_button(gb, cl, checked, t))

                elif widget_type == 'ExclusiveGroupWidget': #change from V1 ExclusiveFrameWidget to V2 ExclusiveGroupWidget, and widgets to children
                    if "children" in item:
                        for sub_widget_name in item["children"]:
                            # Find the sub-widget from dataset_json
                            sub_widget = next((w for w in dataset_json if isinstance(w, dict) and w.get("name") == sub_widget_name), None)
                            #print("sub_children", sub_widget)
                            if sub_widget:
                                create_widget(sub_widget, groupBoxLayout, processed_widgets)

                elif widget_type == 'FreeEditionWidget':
                    labelText = item.get('details', {}).get('text', 'No information')
                    self.labelWidget = QtWidgets.QLabel(labelText, groupBox)
                    flowLayout.addWidget(self.labelWidget)

                elif widget_type == 'GeographicExtentWidget':
                    extentLabels = item['details'].get('extentlabels', [])
                    defaultValues = item['details'].get('default', [])
                    extentLayout = QtWidgets.QFormLayout()
                    groupBoxLayout.addLayout(extentLayout)

                    #for label, default in zip(extentLabels, defaultValues):
                    for key in ['n', 'w', 's', 'e']:  # Specifying the order: north, west, south, east
                        label = extentLabels.get(key, '')  # Get the label text (e.g., "North")
                        default = defaultValues.get(key, '')  # Get the default value (e.g., 90 for north)
                        extentLabel = QtWidgets.QLabel(label, groupBox)
                        extentInput = QtWidgets.QLineEdit(groupBox)
                        extentInput.setText(str(default))
                        self.extent_inputs[key] = extentInput
                        extentInput.textChanged.connect(lambda text, dir=key: self.update_area_input(dir, text, item['name'], 'area'))
                        self.area_input[key] = float(extentInput.text())
                        
                        extentLayout.addRow(extentLabel, extentInput)
                    
                    showGlobeButton = QtWidgets.QPushButton('Map coordinates', groupBox)
                    showGlobeButton.setStyleSheet("margin-top: 20px;")
                    showGlobeButton.setFixedHeight(50)
                    showGlobeButton.clicked.connect(self.open_globe_map)
                    extentLayout.addRow(showGlobeButton)

                    self.geographicExtentMap = extentLayout

                elif widget_type == 'StringListArrayWidget':
                    all_checkboxes = [] # Store all checkboxes across all accordion groups
                    if item['details'].get('accordionGroups', True):
                        groups = item['details'].get('groups', [])
                        
                        for group in groups:
                            flowLayout = FlowLayout()
                            checkboxes = []
                            
                            values = group.get('values', [])

                            for value in values:
                                checkLabel = QtWidgets.QCheckBox(group['labels'][value])
                                #checkLabel.stateChanged.connect(self.update_constraints)
                                flowLayout.addWidget(checkLabel)
                                checkLabel.stateChanged.connect(lambda: update_validation_label(all_checkboxes))  # Connect to validation update
                                checkLabel.stateChanged.connect(lambda state, gb=item['name'], v=value, t=widget_type: self.create_selected_items(gb, v, state, t))
                                checkboxes.append(checkLabel)
                                all_checkboxes.append(checkLabel)  # Add to the global list of all checkboxes
                                self.widgets_store[groupBoxName][value] = checkLabel

                            container_layout = QtWidgets.QVBoxLayout()
                            container_layout.addLayout(flowLayout)
                            
                            self.addButtonSelectCleanAll(container_layout, checkboxes, item['name'], widget_type, values, validation_label)
                            container_layout.setContentsMargins(0, 0, 0, 0)  # Adjust margins if needed
                            container_layout.setSpacing(5)  # Adjust spacing if needed
                            accordion = Accordion(group['label'], container_layout, parent=groupBox)

                            groupBoxLayout.addWidget(accordion)
                        
                    else:
                    # Handle non-accordion case here if needed
                        pass

                elif widget_type == 'LicenceWidget':
                    all_checkboxes = [] # Store all checkboxes across all accordion groups
                    licences_dataset = item.get('details', {}).get('licences', [])
                    accepted_licences = {licence["id"] for licence in licences_list.get("licences", [])}

                    # Create a QGroupBox for "Terms of Use"
                    #groupBox = QtWidgets.QGroupBox(item['label'], self.dialog)
                    #groupBoxLayout = QtWidgets.QVBoxLayout(groupBox)

                    # Iterate over the dataset's required licences
                    for licence in licences_dataset:
                        licence_id = licence["id"]
                        licence_label = licence["label"]
                        licence_revision = licence.get("revision", 1)  # Get revision
                        self.licence_labels[licence_id] = licence_label

                        if licence_id in accepted_licences:
                            # ✅ Already accepted: Add a disabled checkbox
                            checkLabel = QtWidgets.QCheckBox(f"{licence_label} - Accepted ✅", groupBox)
                            checkLabel.setChecked(True)
                            checkLabel.setDisabled(True)  # Prevent unchecking
                            groupBoxLayout.addWidget(checkLabel)
                        else:
                            # ❌ Needs acceptance: Add a button with warning text
                            acceptButton = QtWidgets.QPushButton(f"Accept Terms for {licence_label}", groupBox)
                            acceptButton.setStyleSheet("background-color: #ffcc00; font-weight: bold;")
                            acceptButton.clicked.connect(lambda _, lid=licence_id, rev=licence_revision: AcceptLicences(self).accept_licence(lid, rev))

                            warningLabel = QtWidgets.QLabel("⚠️ You must accept the terms before submitting this request.", groupBox)
                            warningLabel.setStyleSheet("color: red; font-style: italic;")

                            groupBoxLayout.addWidget(acceptButton)
                            groupBoxLayout.addWidget(warningLabel)


        # Create processed_widgets set
        processed_widgets = set()

        if dataset_json is not None:
            for item in dataset_json:
                if isinstance(item, dict):
                    create_widget(item, self.verticalLayout, processed_widgets)
    
        self.create_action_buttons('CDS')



    
    def submit_button_clicked_cds(self):
        if not self.validate_required_fields():
            # Display the error message and return
            self.error_display.display_error_message("Please select all required items.", True)
            return

        # Hide the error message since validation passed
        self.error_display.display_error_message("", False)

        # Prepare the data for download
        self.list_items_download = {
            'dataset': self.dataset_selected,
            'items': self.selected_items
        }

        # Start the download task
        try:
            self.task = DownloadServices.start_cds_download(self.list_items_download, self)
        except Exception as e:
            # Log and display any issues starting the download
            print(f"Error starting download: {e}")
            self.error_display.display_error_message(f"Error: {e}", True)

    '''def submit_button_clicked_cds(self):
        if not self.validate_required_fields():
            self.error_display.display_error_message("Please select all required items.", True)
            #self.error_message_label.setText("Please select all required items.")
            #self.error_message_label.setVisible(True)
        else:
            self.error_display.display_error_message("", True)
            #self.error_message_label.setVisible(True)
            #self.error_message_label.setText("")
            self.list_items_download = {
                'dataset': self.dataset_selected,
                'items': self.selected_items
            }
           
            self.task = DownloadServices.start_cds_download(self.list_items_download, self)  # Start the download'''
        

        
    def set_form_layout_disabled(self, form_layout, disabled):
        if form_layout and form_layout.parent() is not None:
            for i in range(form_layout.count()):
                item = form_layout.itemAt(i)
                if item is not None:
                    widget = item.widget()
                    if widget is not None:
                        widget.setDisabled(disabled)
        
    
    def create_cmcc_widgets(self, dataset_json, section_id):
        widgets_order = dataset_json["widgets_order"]
        widgets = dataset_json["widgets"]
        self.dataset_id = dataset_json['dataset'].get("id")
        self.default_product = section_id  # Get the id section chose
        self.list_items_download = {}
        self.selected_items = {}
        self.area_input = {}
        self.location_input = {}
        self.source_name = 'CMCC'
        
        # Create a dictionary for quick lookup of form data by name
        form_dict = {item["name"]: item for item in widgets}

        # Create a QButtonGroup for mutual exclusivity
        buttonGroup = QtWidgets.QButtonGroup(self.dialog)
        buttonGroup.setExclusive(True)

        def create_widget(item, parent_layout):
            validation_label = None
            #print(f"item in create_widget: {item['details']} (ID: {id(item)})")  # Debugging

            groupBox = QtWidgets.QGroupBox(item['label'], self.dialog)
            groupBoxLayout = QtWidgets.QVBoxLayout()

            if item['name'] == 'area':
                whole_region_radio  = QtWidgets.QRadioButton('Whole available region', groupBox)
                groupBoxLayout.addWidget(whole_region_radio)
                self.labelWidget = QtWidgets.QLabel('With this option selected, the entire available area will be provided', groupBox)
                groupBoxLayout.addWidget(self.labelWidget)
                
                sub_region_radio  = QtWidgets.QRadioButton('Sub-region extraction', groupBox)
                groupBoxLayout.addWidget(sub_region_radio)
                sub_region_radio.toggled.connect(lambda checked, gb=item['name'], v=self.area_input, t=item['type']:
                               self.create_selected_items(gb, v, QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked, t))
                buttonGroup.addButton(whole_region_radio)
                buttonGroup.addButton(sub_region_radio)

                def delayed_initialization():
                    # Connect the radio button to the handler
                    whole_region_radio.setChecked(True)
                    self.handle_global_area_radio_button(True, 'global')

                # Set a timer to call the initialization function after a small delay (e.g., 100 ms)
                QtCore.QTimer.singleShot(500, delayed_initialization)

                whole_region_radio.toggled.connect(lambda checked:self.handle_global_area_radio_button(checked, 'global'))
                sub_region_radio.toggled.connect(lambda checked:self.handle_global_area_radio_button(checked, 'area'))

            if item['name'] == 'location':
                lat_long_radio  = QtWidgets.QRadioButton('Range', groupBox)
                lat_long_radio.toggled.connect(lambda checked, gb=item['name'], v=self.location_input, t='location':
                               self.create_selected_items(gb, v, QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked, t))
                groupBoxLayout.addWidget(lat_long_radio)
                buttonGroup.addButton(lat_long_radio)
                lat_long_radio.toggled.connect(lambda checked:self.handle_global_area_radio_button(checked, 'location'))

            groupBox.setLayout(groupBoxLayout)
            parent_layout.addWidget(groupBox)

            self.group_boxes.append(groupBox)

            flowLayout = FlowLayout()
            groupBoxLayout.addLayout(flowLayout)
            
            if "details" in item:
                details = item["details"]
                widget_parameter = item['parameter']

                def update_validation_label(widgets_list):
                    """Hide or show the validation label based on selection state."""
                    if any(widget.isChecked() for widget in widgets_list):
                        if validation_label:
                            validation_label.setVisible(False)  # Hide the validation message
                    else:
                        if validation_label:
                            validation_label.setVisible(True)  # Show the validation message again    

                if "values" in details:
                    if item['type'] == 'StringList':
                        checkboxes = []
                        checkboxesValue = []

                        for value in details["values"]:
                            #print(f" - {value['label']}: {value['value']}")
                            checkLabel = QtWidgets.QCheckBox(f"{value['label']}", groupBox)
                            flowLayout.addWidget(checkLabel)
                            checkboxes.append(checkLabel)
                            checkLabel.stateChanged.connect(lambda state, gb=item['name'], v=value['value'], t=widget_parameter: self.create_selected_items(gb, v, state, t))
                            checkLabel.stateChanged.connect(lambda: update_validation_label(checkboxes))
                            checkboxesValue.append(value['value'])
                        
                         # Handle "required" attribute by adding a label for required fields       
                        if item.get('required', False):
                            validation_label = QtWidgets.QLabel("This is a required parameter", groupBox)
                            validation_label.setStyleSheet("color: red;")
                            groupBoxLayout.addWidget(validation_label)
                            validation_label.setVisible(True) 

                        self.addButtonSelectCleanAll(groupBoxLayout, checkboxes, item['name'], widget_parameter, checkboxesValue, validation_label)
                    else:
                        first_value = True
                        for value in details["values"]:
                            #print(f" - {value['label']}: {value['value']}")
                            radioLabel = QtWidgets.QRadioButton(f"{value['label']}", groupBox)
                            flowLayout.addWidget(radioLabel)
                            radioLabel.toggled.connect(lambda checked, gb=item['name'], v=value['value'], t=item['type']:
                               self.create_selected_items(gb, v, QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked, t))

                            # Check only the first radio button
                            if first_value:
                                radioLabel.setChecked(True)
                                self.create_selected_items(item['name'], value['value'], 2, widget_parameter)
                                first_value = False

                if "widgets" in details:
                    #print("Widgets:")
                    for sub_widget in details["widgets"]:
                        if sub_widget in form_dict:
                            sub_item = form_dict[sub_widget]
                            if(sub_item['name'] not in ['date_range', 'vertical_range']):
                                create_widget(sub_item, groupBoxLayout)  # Pass the group box layout to nest widgets correctly

                if "fields" in details:
                    
                    if item['type'] in ['geoarea', 'geolocation', 'NumberRange']:
                        extentLayout = QtWidgets.QFormLayout()
                        groupBoxLayout.addLayout(extentLayout)
    
                        for field in details["fields"]:
                            fieldLabel = QtWidgets.QLabel(f"{field['label']}:")
                            rangeInput = QtWidgets.QLineEdit()
                            range_value = field['range'][0] if isinstance(field['range'], list) else field['range'] # Check if field['range'] is a list, and use only the first element if it is
                            rangeInput.setText(str(range_value)) 

                            if field['label'].lower() in ['north', 'south', 'east', 'west']:
                                direction = field['label'].lower()
                                rangeInput.textChanged.connect(lambda text, dir=direction: self.update_area_input(dir, text, item['name'], widget_parameter))
                                self.area_input[direction] = float(rangeInput.text())
                                direction_key = field['label'].lower()[0]  # Get the first letter: n, s, e, w use the short for use the same function we use for copernicus fore remove the params
                                self.extent_inputs[direction_key] = rangeInput
                            elif field['name'] in ['latitude', 'longitude']:
                                direction = field['name']
                                self.location_input[direction] = float(rangeInput.text())
                                rangeInput.textChanged.connect(lambda text, dir=direction: self.update_location_input(dir, text, item['name'], widget_parameter))

                            extentLayout.addRow(fieldLabel, rangeInput)

                        if item['type'] == 'geoarea':
                            showGlobeButton = QtWidgets.QPushButton('Map coordinates', groupBox)
                            showGlobeButton.setStyleSheet("margin-top: 20px;")
                            showGlobeButton.setFixedHeight(50)
                            showGlobeButton.clicked.connect(self.open_globe_map)
                            extentLayout.addRow(showGlobeButton)
                            self.geographicExtentMap = extentLayout

                        if item['type'] == 'geolocation':
                            self.geographicLocationMap = extentLayout


        for widget in widgets_order:
            if widget in form_dict:
                item = form_dict[widget]
                create_widget(item, self.verticalLayout)
        #populate_widgets(dataset_json)
        
        self.create_action_buttons('CMCC')
    
    def update_area_input(self, direction, text, item, widget_parameter): #UUpdate data inside area_input for download For CMCC
        try:
            self.area_input[direction] = float(text)
            self.create_selected_items(item, self.area_input, 2, widget_parameter)
        except ValueError:
            self.area_input[direction] = None

    def update_location_input(self, direction, text, item, widget_parameter): #UUpdate data inside location_input for download For CMCC
        try:
            self.location_input[direction] = float(text)
            self.create_selected_items(item, self.location_input, 2, widget_parameter)
        except ValueError:
            self.location_input[direction] = None


    def submit_button_clicked_cmcc(self):
        if not self.validate_required_fields():
            self.error_display.display_error_message("Please select all required items.", True)
        else:
            self.error_display.display_error_message("", True)
            print("self.dataset_id",  self.dataset_id, self.default_product, self.selected_items)
            self.list_items_download = {
                'id': self.dataset_id,
                'product': self.default_product,
                'items': self.selected_items
            }
            estimate_url = (
                f"https://ddshub.cmcc.it/web/datasets/{self.list_items_download.get('id')}/"
                f"{self.list_items_download.get('product')}/estimate"
            )
            data_service = DataServices(estimate_url)
            response = data_service.postEstimateData(self.selected_items)
            
            if(response):
                if response.get("status") == "OK":
                    self.error_display.display_error_message(response.get("message", "No message provided"), True)
                    #self.error_message_label.setText(response.get("message", "No message provided"))
                    self.task = DownloadServices.start_cmcc_download(self.list_items_download)  # Start the download
                else:
                    print("MESSAGE", response.get("message", "No message provided"))
                    self.error_display.display_error_message(response.get("message", "No message provided"), True)
            else:
                self.error_display.display_error_message("Server Error", True)


    def validate_required_fields(self):
        # Only check if each `validation_label` for required items is hidden
        for group_box in self.group_boxes:
            for widget in group_box.findChildren(QtWidgets.QLabel):
                # Check if it's a validation label and is visible (indicating an unmet required field)
                if widget.text() == "This is a required parameter" and widget.isVisible():
                    return False
        return True

    
    def create_selected_items(self, group_name, label, state, widget_parameter):
        """
        Builds the data structure for download. Handles nested and flat widgets differently.
        """
        # Handle nested structures with `:` in widget_parameter
        if ':' in widget_parameter:
            keys = widget_parameter.split(':')
            main_key = keys[0]
            sub_key = keys[1]
            
            # Initialize main key dictionary if it doesn't exist
            if main_key not in self.selected_items:
                self.selected_items[main_key] = {}

            # Add or remove label based on state
            if state == QtCore.Qt.Checked:
                # Initialize sub-key list if it doesn't exist
                if sub_key not in self.selected_items[main_key]:
                    self.selected_items[main_key][sub_key] = []

                # Add the label to the sub-key list
                if isinstance(label, list):
                    for item in label:
                        if item not in self.selected_items[main_key][sub_key]:
                            self.selected_items[main_key][sub_key].append(item)
                else:
                    if label not in self.selected_items[main_key][sub_key]:
                        self.selected_items[main_key][sub_key].append(label)
            else:
                # Remove the label if unchecked
                if sub_key in self.selected_items[main_key]:
                    if isinstance(label, list):
                        for item in label:
                            if item in self.selected_items[main_key][sub_key]:
                                self.selected_items[main_key][sub_key].remove(item)
                    else:
                        if label in self.selected_items[main_key][sub_key]:
                            self.selected_items[main_key][sub_key].remove(label)
                    # Remove the sub-key if empty
                    if not self.selected_items[main_key][sub_key]:
                        del self.selected_items[main_key][sub_key]

            # Remove the main_key if empty
            if not self.selected_items[main_key]:
                del self.selected_items[main_key]

        # Handle flat structures (non-nested widgets)
        else:
            if state == QtCore.Qt.Checked:
                
                if self.source_name == "CDS" and widget_parameter == "area":
                    if isinstance(label, dict):
                        label = [label.get('n', 0), label.get('w', 0), label.get('s', 0), label.get('e', 0)]
                    self.selected_items[group_name] = label
                elif self.source_name == "CMCC" and widget_parameter in ["area", "location"]:
                    
                    self.selected_items[group_name] = label
                elif widget_parameter in ["StringChoiceWidget", "StringChoice", "FileFormat", "geoarea"]:
                    # Directly assign the label as a string for StringChoiceWidget
                    self.selected_items[group_name] = label  # Assign as a single string
                else:
                    # Ensure the group exists
                    if group_name not in self.selected_items:
                        self.selected_items[group_name] = []

                    # Add label(s) to the group
                    if isinstance(label, list):
                        for item in label:
                            if item not in self.selected_items[group_name]:
                                self.selected_items[group_name].append(item)
                    else:
                        if label not in self.selected_items[group_name]:
                            self.selected_items[group_name].append(label)
            else:
                # Remove items for unchecking
                print("widget_parameter", widget_parameter, label)
                if widget_parameter == "area":
                    del self.selected_items["area"]
                elif widget_parameter in ["StringChoiceWidget", "StringChoice", "FileFormat", "geoarea"]:
                    # Clear single-value widgets when unchecked
                    if self.selected_items.get(group_name) == label:
                        del self.selected_items[group_name]
                else:
                    # Remove the label(s) from the group
                    if group_name in self.selected_items:
                        if isinstance(label, list):
                            for item in label:
                                if item in self.selected_items[group_name]:
                                    self.selected_items[group_name].remove(item)
                        else:
                            if label in self.selected_items[group_name]:
                                self.selected_items[group_name].remove(label)

                        # Remove the group if empty
                        if not self.selected_items[group_name]:
                            del self.selected_items[group_name]

        # Debug output
        print("self.selected_items", widget_parameter, self.source_name, self.selected_items)

        # Call update_constraints for CDS source
        if self.source_name == 'CDS':
            self.update_handler.update_constraints(self.selected_items)
        
        

    def create_action_buttons(self, source_tag): #Create button submit and cancel
        '''if hasattr(self, 'error_message_label') and self.error_message_label is not None:
            self.error_message_label.setParent(None)  # Remove from the parent layout
            del self.error_message_label  # Delete the reference to the old label

        self.error_message_label = QtWidgets.QLabel("")
        self.error_message_label.setStyleSheet("color: red; font-size: 18px;")
        self.error_message_label.setVisible(False)'''
        

        # Create a QGroupBox for the buttons
        self.button_group_box = QtWidgets.QGroupBox("Actions", self.dialog)
        button_layout = QtWidgets.QHBoxLayout()

        # Create the buttons
        submit_button = QtWidgets.QPushButton("Submit")
        submit_button.setStyleSheet("background-color: green; color: white; font-size: 16px; padding: 8px;")
        button_layout.addWidget(submit_button)
        self.button_group_box.setLayout(button_layout)
        self.verticalLayout.addWidget(self.button_group_box)

        self.error_display.display_error_message('', False)

        self.group_boxes.append(self.button_group_box)  # Store only the group box (a QWidget)
        
        if(source_tag == 'CDS'):
            submit_button.clicked.connect(self.submit_button_clicked_cds)
        else:
            submit_button.clicked.connect(self.submit_button_clicked_cmcc)
    


    def handle_global_area_radio_button(self, checked, type_radio):
        print("checked", checked, type_radio)
        if checked:
            if type_radio == 'global':
                if self.labelWidget and not sip.isdeleted(self.labelWidget):
                    self.labelWidget.setDisabled(False)
                if self.geographicExtentMap:
                    self.set_form_layout_disabled(self.geographicExtentMap, True)
                if self.geographicLocationMap:
                    self.set_form_layout_disabled(self.geographicLocationMap, True)
            elif type_radio == 'area':
                if self.labelWidget:
                    self.labelWidget.setDisabled(True)
                if self.geographicExtentMap:
                    self.set_form_layout_disabled(self.geographicExtentMap, False)
                if self.geographicLocationMap:
                    self.set_form_layout_disabled(self.geographicLocationMap, True)
            elif type_radio == 'location':
                if self.labelWidget and not sip.isdeleted(self.labelWidget):
                    self.labelWidget.setDisabled(True)
                if self.geographicExtentMap and self.geographicExtentMap.parent() is not None:
                    self.set_form_layout_disabled(self.geographicExtentMap, True)
                if self.geographicLocationMap and self.geographicLocationMap.parent() is not None:
                    self.set_form_layout_disabled(self.geographicLocationMap, False)


    def addButtonSelectCleanAll(self, groupBoxLayout, checkboxes, group_name, widget_parameter, values, validation_label=None):
            
            buttonLayout = FlowLayout()
            #buttonLayout = QtWidgets.QHBoxLayout()
            buttonLayout.setContentsMargins(0, 0, 0, 0)
            buttonLayout.setSpacing(5)
            selectAllButton = QtWidgets.QPushButton("Select All", self.dialog)
            selectAllButton.clicked.connect(lambda: self.select_all(checkboxes, group_name, widget_parameter, values, validation_label))

            clearAllButton = QtWidgets.QPushButton("Clear All", self.dialog)
            clearAllButton.clicked.connect(lambda: self.clear_all(checkboxes, group_name, widget_parameter, values, validation_label))

            buttonLayout.addWidget(selectAllButton)
            buttonLayout.addWidget(clearAllButton)
            groupBoxLayout.addLayout(buttonLayout)



    def select_all(self, checkboxes, group_name, widget_parameter, values, validation_label=None):
        self.batch_update = True
        try:
            selected_values = []

            for checkbox, value in zip(checkboxes, values):
                if checkbox.isEnabled():
                    checkbox.blockSignals(True)  # Temporarily block signals
                    checkbox.setChecked(True)  # Visually check the checkbox
                    checkbox.blockSignals(False)
                    selected_values.append(value)

            if validation_label:
                validation_label.setVisible(False)
                
        finally:
            self.batch_update = False

        self.create_selected_items(group_name, selected_values, QtCore.Qt.Checked, widget_parameter)


    def clear_all(self, checkboxes, group_name, widget_parameter,values, validation_label=None):
        self.batch_update = True
        try:
            for checkbox in checkboxes:
                checkbox.blockSignals(True)  # Temporarily block signals
                checkbox.setChecked(False)  # Visually uncheck the checkbox
                checkbox.blockSignals(False)

            if validation_label:
                validation_label.setVisible(True)
                
        finally:
            self.batch_update = False

        self.create_selected_items(group_name, values, QtCore.Qt.Unchecked, widget_parameter)



    def disconnect_signals(self, widgets):
        """
        Disconnect all signals from the provided widgets.
        """
        if isinstance(widgets, QtWidgets.QWidget):  # Handle single widget
            widgets = [widgets]  # Wrap in a list to make it iterable

        for widget in widgets:
            if isinstance(widget, QtWidgets.QCheckBox):  # Add other widget types if needed
                try:
                    widget.stateChanged.disconnect()  # Disconnect stateChanged signal
                except TypeError:
                    pass  # Ignore if no signal is connected
            elif isinstance(widget, QtWidgets.QRadioButton):  # Handle radio buttons
                try:
                    widget.toggled.disconnect()  # Disconnect toggled signal
                except TypeError:
                    pass


    def remove_inner_group_box(self):
        """
        Removes all group boxes from the vertical layout and clears references.
        """
        print("Starting removal of group boxes...")
        if self.error_display.error_message_label is not None: #hasattr(self, 'error_message_label') and          
            if self.error_display.error_message_label.parent() is not None:
                # Remove it from the layout if it has a parent
                self.error_display.error_message_label.setParent(None)
            self.error_display.error_message_label.deleteLater()  # Schedule the label for deletion
            self.error_display.error_message_label = None  # Clear the reference
        
        #remaining_group_boxes = []
        if self.group_boxes:
            for groupBox in self.group_boxes:
                
                #if isinstance(groupBox, QtWidgets.QWidget):     
                if isinstance(groupBox, QtWidgets.QGroupBox):  # Check if it's a QGroupBox
                   
                    # Disconnect signals for all child widgets
                    child_widgets = groupBox.findChildren(QtWidgets.QWidget)
                    for child in child_widgets:
                        self.disconnect_signals(child)

                    # Remove the group box from the layout
                    if groupBox.parent() is not None:
                        self.verticalLayout.removeWidget(groupBox)
                    groupBox.deleteLater()

            # Clear the list since we've removed all group boxes
            self.group_boxes.clear()

        # Update the group_boxes list to only keep the excluded group
        #self.group_boxes = remaining_group_boxes
        self.widgets_store.clear()
        self.verticalLayout.update()

        print(f"Remaining group boxes after cleanup: {[box.title() for box in self.group_boxes]}")
        print(f"After removal: {len(self.group_boxes)} widgets in layout.")
        print(f"Widgets store after cleanup: {self.widgets_store}")


    def open_globe_map(self):
        """Open the Globe Map Viewer on button click."""
        self.globe_form = GlobeMapForm()  # Initialize the GlobeMapForm class
        self.globe_form.coordinates_saved.connect(self.update_extent_fields)  # Connect the signal
        self.globe_form.show()            # Show the form with the map

    def update_extent_fields(self, north, west, south, east):
        """Update the QLineEdit fields with the coordinates from the map."""
        print(f"Received coordinates: North: {north}, West: {west}, South: {south}, East: {east}")
        self.extent_inputs['n'].setText(str(north))
        self.extent_inputs['w'].setText(str(west))
        self.extent_inputs['s'].setText(str(south))
        self.extent_inputs['e'].setText(str(east))



        

