
from qgis.core import  QgsMessageLog
from ..services.data_services import DataServices
from qgis.PyQt import QtWidgets



class AcceptLicences:
    def __init__(self, widget_creator):
        """
        AcceptLicences class handles accepting licenses and updating the UI.
        
        :param widget_creator: Reference to the main UI class (WidgetCreator)
        """
        self.widget_creator = widget_creator  # Store reference to the main UI


    def accept_licence(self, licence_id, revision):
        """
        Calls DataServices to send a PUT request to accept a licence.
        Updates the UI if the request is successful.
        """
        if not licence_id or not revision:
            QgsMessageLog.logMessage("Error", f"Missing licence ID or revision.")
            return

        # Initialize DataServices and make PUT request
        service = DataServices(url="https://cds.climate.copernicus.eu/api/profiles/v1/account/licences/")
        response = service.putLicences(licence_id, revision)

        if response:
            self.refresh_licence_ui(licence_id)  # Refresh the UI
        else:
            QgsMessageLog.logMessage("Request Failed", f"Could not accept licence: {licence_id}")

    
    def refresh_licence_ui(self, licence_id):
        """
        Refreshes the UI to replace the 'Accept Terms' button with an accepted checkbox.
        """
        licence_label = self.widget_creator.licence_labels.get(licence_id, licence_id)  # Fallback to ID if label not found

        for groupBox in self.widget_creator.group_boxes:  # Iterate through UI group boxes
            layout = groupBox.layout()

            for i in reversed(range(layout.count())):  # Iterate over widgets inside the group box
                widget = layout.itemAt(i).widget()
                
                if widget is None:
                    #print(f"Skipping empty widget at index {i}")
                    continue

                widget_text = widget.text() if hasattr(widget, "text") else " No text attribute"
             
                if isinstance(widget, QtWidgets.QPushButton) and licence_label in widget_text:
                    # Remove the button and warning label
                    widget.deleteLater()

                    # Search and remove the warning label in the whole layout
                    for j in range(layout.count()):
                        warning_label = layout.itemAt(j).widget()
                        if isinstance(warning_label, QtWidgets.QLabel) and "You must accept" in warning_label.text():
                            print(f"🗑️ Removing warning label: {warning_label.text()}")
                            warning_label.deleteLater()
                            break  # Stop after removing the first matching label

                    # Add the accepted checkbox
                    accepted_checkbox = QtWidgets.QCheckBox(f"{licence_id} - Accepted ✅", groupBox)
                    accepted_checkbox.setChecked(True)
                    accepted_checkbox.setDisabled(True)  # Prevent unchecking
                    layout.addWidget(accepted_checkbox)

                    # Stop searching once we update the relevant licence
                    return