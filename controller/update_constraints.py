
from qgis.PyQt import QtWidgets
from PyQt5 import QtCore
import json
from ..services.data_services import DataServices
import sip

class UpdateConstraints:
    def __init__(self, widget_creator, url_data_constraints):
        self.selected_items = {}
        self.url_data_constraints = url_data_constraints
        self.service_data_constraints = DataServices(self.url_data_constraints)
        self.widget_creator = widget_creator  # Store references to widgets

    def handle_radio_button(self, group_name, label, state, widget_type):
        if state:
            # Call update_constraints only if the radio button is checked
            self.update_constraints(group_name, label, state, widget_type)

    #def update_constraints(self, group_name, label, state, widget_type):
    def update_constraints(self, items):
            """
            Updates the constraints based on the group name and label.
            - group_name: str, the name of the group (e.g., 'variable', 'experiment').
            - label: str, the label of the checkbox.
            - state: int, the state of the checkbox (checked or unchecked).
            """

            #print("send dataaaaaaaa", items)
            
            '''if group_name not in self.selected_items:
                self.selected_items[group_name] = []

            if state == QtCore.Qt.Checked:
                if label not in self.selected_items[group_name]:
                    self.selected_items[group_name].append(label)
            else:
                # If the state is unchecked, remove the label from the corresponding list
                if group_name in self.selected_items and label in self.selected_items[group_name]:
                    self.selected_items[group_name].remove(label)'''

            # Debug print to check current selections
            #print(f"Updated selections: {self.selected_items}")
            self.send_data(items)


    def send_data(self, items):
        if items:
            # Wrap the selected items in the required format for POST request
            post_data = {"inputs": items}
            #print("post_data:", post_data)

            response = self.service_data_constraints.postConstraintsData(post_data)
            if response:
                #print("Data sent successfully response:", response)
                self.update_widgets_based_on_response(response)
            else:
                print("Failed to send data.")



    '''def update_widgets_based_on_response(self, response):
        """
        Updates the widgets (e.g., checkboxes) based on the server response.
        
        :param response: A dictionary containing available options from the server.
        """

        for group_name, available_options in response.items():
            print("Keys in widgets_store:", self.widget_creator.widgets_store.keys())
            if group_name in self.widget_creator.widgets_store:
              
                for option, widget in self.widget_creator.widgets_store[group_name].items():
                    
                    if option in available_options:
                        widget.setEnabled(True)  # Enable if it's in the response
                    else:
                        widget.setEnabled(False)  # Disable if it's not in the response'''
    
    def update_widgets_based_on_response(self, response):

        for group_name, available_options in response.items():
           # print(f"Processing group: {group_name}, Available options: {available_options}")
            # Check if the group exists in the widgets_store
            if group_name in self.widget_creator.widgets_store:
                group_widgets = self.widget_creator.widgets_store[group_name]

                #print(f"Group widgets for '{group_name}': {list(group_widgets.keys())}")

                # Check if the group has a validation label
                validation_label = getattr(self.widget_creator, "validation_labels", {}).get(group_name, None)
                # Manage the visibility of the validation label
                if validation_label:
                    if not available_options:
                        validation_label.setVisible(False)  
                    #else:
                     #   validation_label.setVisible(True) 
                
                # Iterate over each option and its corresponding widget in the group
                for option, widget in list(group_widgets.items()):
                    if widget is None or not widget.isVisible():  # Check validity
                        #print(f"Skipping deleted or invalid widget for option: {option}")
                        continue

                    if option in available_options:
                        widget.setEnabled(True)  # Enable if it's in the response
                    else:
                        widget.setChecked(False)
                        widget.setEnabled(False)  # Disable if it's not in the response
                        
            else:
                print(f"Group '{group_name}' not found in widgets_store.")

        
        