


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



class Ui(*uic.loadUiType(str(CURRENT_DIR / 'main_window.ui'))):
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
        self.set_fa_fv()
        self.set_sds()
        self.set_sd1()
        self.update_sa_plot()
        self.calculate_cs()
        self.create_connections()

    def set_plot_widget(self):
        self.graphWidget = pg.PlotWidget()
        self.spectral.addWidget(self.graphWidget)
        self.graphWidget.setLabel('bottom', 'Period T', units='sec.')
        self.graphWidget.setLabel('left', 'Sa')
        self.graphWidget.setXRange(0, 2, padding=0)
        # self.graphWidget.setYRange(0, 3, padding=0)
        self.graphWidget.showGrid(x=True, y=True)

    def create_connections(self):
        self.site_class_combo.currentIndexChanged.connect(self.set_fa_fv)
        self.province.currentIndexChanged.connect(self.update_cities)
        self.city.currentIndexChanged.connect(self.set_pga_ss_s1)
        self.approx_t.clicked.connect(self.approx_t_clicked)
        self.ct.valueChanged.connect(self.set_period)
        self.x.valueChanged.connect(self.set_period)
        self.H.valueChanged.connect(self.set_period)
        self.ss.valueChanged.connect(self.set_fa)
        self.ss.valueChanged.connect(self.set_sds)
        self.s1.valueChanged.connect(self.set_fv)
        self.s1.valueChanged.connect(self.set_sd1)
        self.fa.valueChanged.connect(self.set_sds)
        self.fv.valueChanged.connect(self.set_sd1)
        self.sds.valueChanged.connect(self.update_sa_plot)
        self.tl.valueChanged.connect(self.update_sa_plot)
        self.sd1.valueChanged.connect(self.update_sa_plot)
        # self.systems_treeview.expanded.connect(self.tree_expanded)
        self.systems_treeview.clicked.connect(self.set_system_property)
        # calculate cs
        self.sds.valueChanged.connect(self.calculate_cs)
        self.sd1.valueChanged.connect(self.calculate_cs)
        self.s1.valueChanged.connect(self.calculate_cs)
        self.R.valueChanged.connect(self.calculate_cs)
        self.I.currentIndexChanged.connect(self.calculate_cs)
        self.period.valueChanged.connect(self.calculate_cs)
        self.tl.valueChanged.connect(self.calculate_cs)
        self.site_class_combo.currentIndexChanged.connect(self.calculate_cs)

    def set_system_property(self):
        index = self.systems_treeview.selectedIndexes()[0]
        if index.isValid():
            data = index.internalPointer()._data
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
        csv_path = CURRENT_DIR / 'PGA-Ss-S1.csv'
        provinces = []
        with open(csv_path, 'r') as f:
            reader = csv.reader(f, delimiter=',')
            for row in reader:
                if row[1] == 'PGA':
                    provinces.append(row[0])
        self.province.addItems(provinces)

    def update_cities(self):
        province = self.province.currentText()
        csv_path = CURRENT_DIR / 'PGA-Ss-S1.csv'
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

    def set_system_treeview(self):
        items = {}

        # Set some random data:
        csv_path = Path(__file__).parent / 'systems.csv'
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
        tl = self.tl.value()
        ts = sd1 / sds
        t0 = 0.2 * ts
        sa_values = []
        x = np.arange(0, 2, .005)
        for t in x:
            if t < t0:
                sa = sds * (0.4 + 0.6 * t / t0)
            elif t0 <= t <= ts:
                sa = sds
            elif ts < t < tl:
                sa = sd1 / t
            elif t >= tl:
                sa = sd1 * tl / t ** 2
            sa_values.append(sa)
        self.graphWidget.clear()
        self.graphWidget.addItem(self.plot_item(x, np.array(sa_values)))
        self.graphWidget.setYRange(0, sds * 1.05, padding=0)

    def set_fa(self):
        ss = self.ss.value()
        site_class = self.site_class_combo.currentText()
        fa = self.forecast_fa_fv(ss, site_class, 'fa.csv')
        if fa is not None:
            self.fa.setValue(fa)
    
    def set_fv(self):
        s1 = self.s1.value()
        site_class = self.site_class_combo.currentText()
        fv = self.forecast_fa_fv(s1, site_class, 'fv.csv')
        if fv is not None:
            self.fv.setValue(fv)

    def set_fa_fv(self):
        site_class = self.site_class_combo.currentText()
        if site_class == 'F':
            QtWidgets.QMessageBox.information(None, 'caution', 'Fa and Fv values shall be determined in accordance with Section 11.4.7 of ASCE 7.')
            return
        self.set_fa()
        self.set_fv()

    def forecast_fa_fv(self, ss, site_class, filename='fa.csv'):
        if site_class == 'F':
            return None
        fas = dict()
        with open(str(CURRENT_DIR / filename)) as f:
            reader = csv.reader(f, delimiter=',')
            ss_limits = reader.__next__()[1:]
            for row in reader:
                if row[0] != 'F':
                    fas[row[0]] = [float(i) for i in row[1:]]
            ss_limits = [float(i) for i in ss_limits]
            if ss in ss_limits:
                i = ss_limits.index(ss)
                fa = fas[site_class][i]
            else:
                ss_limits.append(ss)
                ss_limits = sorted(ss_limits)
                ss_i = ss_limits.index(ss)
                if ss_i == 0:
                    fa = fas[site_class][0]
                elif ss_i == len(ss_limits) - 1:
                    fa = fas[site_class][-1]
                else:
                    ss_lower = ss_limits[ss_i - 1]
                    ss_upper = ss_limits[ss_i + 1]
                    fa_lower = fas[site_class][ss_i - 1]
                    fa_upper = fas[site_class][ss_i] # because we add ss to ss_limits
                    fa = (fa_upper - fa_lower) / (ss_upper - ss_lower) * (ss - ss_lower) + fa_lower
        return fa

    def calculate_cs(self):
        sds = self.sds.value()
        r = self.R.value()
        i = float(self.I.currentText())
        csi = sds / (r / i)
        # check with Eq 12.8-3 or 12.8-4
        t = self.period.value()
        tl = self.tl.value()
        sd1 = self.sd1.value()
        if t <= tl:
            cs1 = sd1 / (r * t / i)
        elif t > tl:
            cs1 = sd1 * tl / (r * t ** 2 / i)
        # section 11.4.8 Exception 2
        cs2 = 0
        site_class = self.site_class_combo.currentText()
        s1 = self.s1.value()
        if site_class == 'D' and s1 >= 0.2:
            if t <= tl:
                if t <= 1.5:
                    cs2 = sds / (r / i)
                elif t > 1.5:
                    cs2 = 1.5 * sds / (r / i) ** t
        # Eq 12.8-5
        cs_min = max(0.044 * sds * i, 0.01)
        # Eq 12.8-6
        cs3 = 0
        if s1 >= 0.6:
            cs3 = 0.5 * s1 / (r / i)
        cs = max(csi, cs1, cs2, cs3, cs_min)
        self.cs_lineedit.setText(f'Cs = {cs:.4f}')
        return cs


if __name__ == "__main__":
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())