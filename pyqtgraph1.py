


import os
import sys

from PyQt5 import  QtWidgets, uic, QtCore
import pyqtgraph as pg

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))



class Ui(*uic.loadUiType(os.path.join(CURRENT_DIR, "pyqtgraph_window.ui"))):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_plot_widget()
        self.create_connections()

    def set_plot_widget(self):
        self.graphWidget = pg.PlotWidget()
        self.spectral.addWidget(self.graphWidget)
        self.graphWidget.setLabel('bottom', 'Period T', units='sec.')
        self.graphWidget.setLabel('left', 'Sa')

    def create_connections(self):
        self.site_class_combo.currentIndexChanged.connect(self.update_ui)
        self.approx_t.clicked.connect(self.approx_t_clicked)
        self.ct.valueChanged.connect(self.set_period)
        self.x.valueChanged.connect(self.set_period)
        self.H.valueChanged.connect(self.set_period)

    def set_period(self):
        ct = self.ct.value()
        x = self.x.value()
        h = self.H.value()
        t = ct * h ** x
        self.period.setValue(t)

    def approx_t_clicked(self):
        if self.approx_t.isChecked():
            self.ct.setEnabled(True)
            self.x.setEnabled(True)
            self.H.setEnabled(True)
            self.period.setEnabled(False)
            self.set_period()
        else:
            self.ct.setEnabled(False)
            self.x.setEnabled(False)
            self.H.setEnabled(False)
            self.period.setEnabled(True)

    def update_ui(self):
        print(self.site_class_combo.currentText())

    def plot_item(self, x, y, color='r'):
        pen = pg.mkPen(color, width=2)
        finitecurve = pg.PlotDataItem(x, y, connect="finite", pen=pen)
        return finitecurve


if __name__ == "__main__":
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    x, y = [0, 1, 5, 10], [0, 1, 2, 7]
    window.graphWidget.setXRange(-0.2 * min(x), 1.2 * max(x))
    window.graphWidget.setYRange(-0.2 * min(y), 1.2 * max(y))
    window.graphWidget.addItem(window.plot_item(x, y))
    window.show()
    sys.exit(app.exec_())