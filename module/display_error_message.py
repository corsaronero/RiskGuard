
from qgis.PyQt import QtWidgets


class DisplayErrorMessage:
    def __init__(self, vertical_layout, parent=None):
        self.vertical_layout = vertical_layout
        self.error_message_label = None
        self.parent = parent

        # Initialize the error message label
        self.create_error_message_label()

    def create_error_message_label(self):
        """Create the error message label if it doesn't already exist."""
        if self.error_message_label is None:
            self.error_message_label = QtWidgets.QLabel("", self.parent)
            self.error_message_label.setStyleSheet("color: red; font-size: 18px;")
            self.error_message_label.setVisible(False)
            self.vertical_layout.addWidget(self.error_message_label)
        else:
            print(f"Reusing existing error_message_label: {id(self.error_message_label)}")


    def display_error_message(self, message, visibility=True):
        # Ensure the label exists
        self.create_error_message_label()

        # Update the label text and visibility
        self.error_message_label.setText(message)
        self.error_message_label.setVisible(visibility)