


# import os
import sys
import csv
from pathlib import Path

import numpy as np

from PyQt5 import  QtWidgets, uic, QtCore
from PyQt5.QtCore import QModelIndex

import pyqtgraph as pg

import treeview

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

CURRENT_DIR = Path(__file__).parent



class Ui(*uic.loadUiType(str(CURRENT_DIR / 'widgets' / 'main_window.ui'))):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cities_pga = None
        self.set_plot_widget()
        self.set_system_treeview()
        self.tree_expanded()
        self.fill_province()
        self.update_cities()
        self.set_pga_ss_s1()
        self.set_sds()
        self.set_sd1()
        self.update_sa_plot()
        self.create_connections()

    def set_plot_widget(self):
        self.graphWidget = pg.PlotWidget()
        self.spectral.addWidget(self.graphWidget)
        self.graphWidget.setLabel('bottom', 'Period T', units='sec.')
        self.graphWidget.setLabel('left', 'Sa')
        self.graphWidget.setXRange(0, 4.5, padding=0)
        self.graphWidget.setYRange(0, 3, padding=0)
        self.graphWidget.showGrid(x=True, y=True)

    def create_connections(self):
        self.site_class_combo.currentIndexChanged.connect(self.update_ui)
        self.province.currentIndexChanged.connect(self.update_cities)
        self.city.currentIndexChanged.connect(self.set_pga_ss_s1)
        self.approx_t.clicked.connect(self.approx_t_clicked)
        self.ct.valueChanged.connect(self.set_period)
        self.x.valueChanged.connect(self.set_period)
        self.H.valueChanged.connect(self.set_period)
        self.ss.valueChanged.connect(self.set_sds)
        self.s1.valueChanged.connect(self.set_sd1)
        self.fa.valueChanged.connect(self.set_sds)
        self.fv.valueChanged.connect(self.set_sd1)
        self.sds.valueChanged.connect(self.update_sa_plot)
        self.sd1.valueChanged.connect(self.update_sa_plot)
        # self.systems_treeview.expanded.connect(self.tree_expanded)
        self.systems_treeview.clicked.connect(self.set_system_property)

    def set_system_property(self):
        index = self.systems_treeview.selectedIndexes()[0]
        if index.isValid():
            data = index.internalPointer()._data
            print(data)
            if len(data) == 1:
                return
            try:
                r = float(data[2])
                omega = float(data[3])
                cd = float(data[4])
                self.R.setValue(r)
                self.omega.setValue(omega)
                self.cd.setValue(cd)
            except:
                pass

    def set_sds(self):
        fa = self.fa.value()
        ss = self.ss.value()
        sds = (2 / 3) * fa * ss
        self.sds.setValue(sds)
    
    def set_sd1(self):
        fv = self.fv.value()
        s1 = self.s1.value()
        sd1 = (2 / 3) * fv * s1
        self.sd1.setValue(sd1)

    def tree_expanded(self):
        for column in range(1, self.systems_treeview.model().columnCount(
                            QModelIndex()) - 1):
            self.systems_treeview.resizeColumnToContents(column)
    
    def fill_province(self):
        csv_path = CURRENT_DIR / 'data' / 'PGA-Ss-S1.csv'
        provinces = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if row[1] == 'PGA':
                    provinces.append(row[0])
        self.province.addItems(provinces)

    def update_cities(self):
        province = self.province.currentText()
        csv_path = CURRENT_DIR / 'data' / 'PGA-Ss-S1.csv'
        cities_pga = dict()
        found = False
        with open(csv_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if found:
                    if row[1] != 'PGA':
                        cities_pga[row[0]] = {
                                        'PGA': row[1],
                                        'Ss': row[2],
                                        'S1': row[3],
                                        }
                    else:
                        break
                elif row[1] == 'PGA' and row[0] == province:
                    found = True
        self.city.clear()
        self.city.addItems(list(cities_pga.keys()))
        self.cities_pga = cities_pga
        self.set_pga_ss_s1()

    def set_pga_ss_s1(self):
        city = self.city.currentText()
        d = self.cities_pga.get(city, None)
        if d is None:
            return
        self.pga.setValue(float(d['PGA']))
        self.ss.setValue(float(d['Ss']))
        self.s1.setValue(float(d['S1']))


        

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

    def set_system_treeview(self):
        items = {}

        # Set some random data:
        csv_path = Path(__file__).parent / 'data' / 'systems.csv'
        with open(csv_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if row[0][0] in 'ABCDEFGH':
                    i = row[0]
                    # root = items.get(i, None)
                    # if root is None:
                    root = treeview.CustomNode(i)
                    items[i] = root
                    if row[0][0] not in 'FH':
                        continue

                root.addChild(treeview.CustomNode(row))

        self.systems_treeview.setModel(treeview.CustomModel(list(items.values()), headers=('System', 'ASCE 7 Section', 'R', 'Omega', 'Cd', 'B', 'C', 'D')))
        self.systems_treeview.setColumnWidth(0, 400)


    def plot_item(self, x, y, color='r'):
        pen = pg.mkPen(color, width=2)
        finitecurve = pg.PlotDataItem(x, y, connect="finite", pen=pen)
        return finitecurve

    def update_sa_plot(self):
        sds = self.sds.value()
        sd1 = self.sd1.value()
        ts = sd1 / sds
        t0 = 0.2 * ts
        sa_values = []
        x = np.arange(0, 4.5, .05)
        for t in x:
            if t < t0:
                sa = sds * (0.4 + 0.6 * t / t0)
            elif t0 <= t <= ts:
                sa = sds
            elif t > ts:
                sa = sd1 / t
            sa_values.append(sa)
        self.graphWidget.clear()
        self.graphWidget.addItem(self.plot_item(x, np.array(sa_values)))






if __name__ == "__main__":
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())