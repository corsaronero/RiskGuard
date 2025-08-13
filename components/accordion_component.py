from PyQt5 import QtWidgets, QtCore
from ..flow_layout import FlowLayout

class Accordion(QtWidgets.QWidget):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)

        self.toggle_button = QtWidgets.QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.toggled.connect(self.toggle)

        self.content_area = QtWidgets.QWidget()
        self.content_area.setLayout(content)
        self.content_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.content_area.setMaximumHeight(0)

        # Create a vertical layout for the accordion
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(5)

        self.content_area.setContentsMargins(20, 0, 0, 0)
        
        self.anim = QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEasingCurve(QtCore.QEasingCurve.InOutQuart)


    def toggle(self, checked):
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)

        # Update content height after the layout has been set up
        self.content_area.adjustSize()
        self.content_height = self.content_area.sizeHint().height()
        
        start_value = self.content_area.maximumHeight()
        end_value = self.content_height if checked else 0

        self.anim.stop()
        self.anim.setStartValue(start_value)
        self.anim.setEndValue(end_value)
        self.anim.start()