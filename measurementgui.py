#!/usr/bin/env python3
import sys

from PyQt5.QtChart import QChart
from PyQt5.QtCore import QObject, QUrl, Qt, pyqtProperty, pyqtSignal, QThread, QMetaObject
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQuick import QQuickView
import time, os
from tools import *
import argparse


class MyThread(QThread):
    def __init__(self, proces, period=0.2):
        super(QThread, self).__init__()
        #QThread.__init__(self)
        self.proc = proces
        self.period = period

    def run(self):
        while True:
            if self.period:
                time.sleep(self.period)
            self.proc()


class Chart(QChart):
    def __init__(self, parent=None):
        QChart.__init__(self, parent)
        self._name = ""
        self.color = QColor()

    def get_color(self):
        return self._name

    def set_color(self):
        self.color.setBlue(100)

    @pyqtProperty('QString')
    def name(self):
        return self._name

    # Define the setter of the 'name' property.
    @name.setter
    def name(self, name):
        self._name = name

class ChildObject(QObject):
    def __init__(self, gauge):
        self.obj = gauge
        self.val = 0

    def set_val(self, val):
        self.obj.setProperty('gauge_value', val)

class ChartCtrl(QObject):
    def __init__(self, chartobj):
        self.chart = chartobj
        self.chart_index = 0
        self.init_chart()

    def init_chart(self):
        self.chart_data = []
        for i in range(100):
            self.chart.setProperty('x_new', i)
            self.chart.setProperty('y_new', 0)
            QMetaObject.invokeMethod(self.chart, "init_chart", Qt.DirectConnection)
            self.chart_data.append(0)
        self.chart_index = 0
        self.chart_len = len(self.chart_data)

    def chart_plot(self):
        for i in range(self.chart_len):
            val = self.chart_data[(self.chart_index + i) % self.chart_len ]
            self.chart.setProperty('x_new', i)
            self.chart.setProperty('y_new', val)
            QMetaObject.invokeMethod(self.chart, "overwrite_chart", Qt.DirectConnection)
        self.chart_index = (self.chart_index + 1) % self.chart_len
        self.chart_data[self.chart_index] = self.val

def mean(data, skip=1):
    local_data = data[::skip]
    l = len(local_data)
    mean = 0
    for i in local_data:
        mean += i
    return float(mean)/l if l else 0

class MeasurementGui(QQuickView):
    chart_move_signal = pyqtSignal()
    gauge_update_signal = pyqtSignal()

    def __init__(self, parent=None, qml=None, eth_name=None, units="mbps", direction="rx", max_val=45,
                 meas_name="NBIOT UL [kbps]", refresh_rate=10):
        super(MeasurementGui, self).__init__()
        qml = os.getcwd()
        qml = os.path.join(qml, 'full_gauge.qml')
        self.units = units
        if units == "kbps":
            self.div_factor = 1000
        if units == "mbps":
            self.div_factor = 1000000
        self.meas_name = meas_name
        self.direction = direction
        self.max_tput = max_val
        self.eth_name = eth_name
        self.setSource(QUrl(qml))
        self.setParent(parent)
        self.val = 0
        self.marg = 0
        self.chart_data = []
        self.gauge = self.findChild(QObject, 'test_gauge')
        self.main_win = self.findChild(QObject, 'main_win')
        self.chart = self.findChild(QObject, 'chart_view')
        self.set_title()
        self.set_units(units)
        self.set_max_val_for_plots(self.max_tput)
        self.init_chart()
        self.gauge_update_signal.connect(self.gauge_update)
        self.chart_move_signal.connect(self.chart_plot)
        self.thr = MyThread(self.gauge_update_signal.emit, period=1.0/refresh_rate)
        self.chart_thr = MyThread(self.chart_move_signal.emit, period=1.0/refresh_rate)
        self.chart_thr.start()
        self.thr.start()
        self.setColor(Qt.transparent)
        self.chart_index = 0
        self.samples_taken = 0
        self.av_kbps = 0
        self.peak_kbps = 0
        self.eth_collection = 10 * [0]
        self.eth_avg_cnt = len(self.eth_collection)
        self.eth_collection_index = 0
        self.eth_recv_bytes = 0
        self.eth_recv_rate = 0
        self.eth_meas_rate = 4/refresh_rate
        self.eth_thr = MyThread(self.get_eth_stats, period=self.eth_meas_rate)
        self.eth_thr.start()

    def set_title(self):
        self.main_win.setProperty("title", self.meas_name)

    def get_eth_stats(self):
        stats = GetNetworkInterfaces(self.eth_name)
        self.eth_recv_rate = float((stats[self.direction]['bytes'] - self.eth_recv_bytes))/self.eth_meas_rate
        self.eth_recv_bytes = stats[self.direction]['bytes']
        self.eth_collection[self.eth_collection_index] = self.eth_recv_rate
        self.eth_collection_index = (self.eth_collection_index + 1) % self.eth_avg_cnt

    def get_eth_rate_mean(self):
        return mean(self.eth_collection)

    def set_units(self, units):
        self.main_win.setProperty('units', " {}".format(units))

    def set_max_val_for_plots(self, val):
        self.main_win.setProperty('max_tput', val)

    def init_chart(self):
        for i in range(100):
            self.chart.setProperty('x_new', i)
            self.chart.setProperty('y_new', 0)
            QMetaObject.invokeMethod(self.chart, "init_chart", Qt.DirectConnection)
            self.chart_data.append(self.max_tput/2)
        self.chart_index = 0
        self.chart_len = len(self.chart_data)

    # def chart_set(self):
    #     x_old = self.chart_index
    #     y_old = self.chart_data[self.chart_index]
    #     x_new = self.chart_index
    #     self.chart_data[self.chart_index] = self.val
    #     y_new = self.chart_data[self.chart_index]
    #
    #     self.chart.setProperty('x_old', x_old)
    #     self.chart.setProperty('y_old', y_old)
    #     self.chart_index = (self.chart_index + 1) % self.chart_len
    #     self.chart.setProperty('x_new', x_new)
    #     self.chart.setProperty('y_new', y_new)
    #     QMetaObject.invokeMethod(self.chart, "update_chart", Qt.DirectConnection)


    def chart_plot(self):
        for i in range(self.chart_len):
            val = self.chart_data[(self.chart_index + i) % self.chart_len ]
            self.chart.setProperty('x_new', i)
            self.chart.setProperty('y_new', val)
            QMetaObject.invokeMethod(self.chart, "overwrite_chart", Qt.DirectConnection)
        self.chart_index = (self.chart_index + 1) % self.chart_len
        self.samples_taken += 1 if self.samples_taken < self.chart_len else 0
        self.chart_data[self.chart_index] = self.val

    def gauge_update(self):
        self.av_kbps = mean(self.chart_data[0:self.samples_taken-1])
        self.gauge.setProperty('gauge_value', self.av_kbps)
        self.val = (self.get_eth_rate_mean()*8)/self.div_factor


class MGauge(QQuickView):
    update_sig = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(MGauge, self).__init__(*args, **kwargs)

        self._value = 0

    @pyqtProperty(int, notify=update_sig)
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = v
        self.update_sig.emit()

    def update(self, v):
        self._value = v
        self.update_sig.emit()

def start_main_gui(args):
    app = QApplication(sys.argv)

    # gauge = MGauge()
    # engine = QQmlApplicationEngine()
    # engine.rootContext().setContextProperty('mgauge', gauge)
    # engine.load(qml)
    # r = engine.rootObjects()[0]

    main_w = MeasurementGui(eth_name=args.eth, units=args.unit, direction=args.dir, max_val=args.max,
                            meas_name=args.title, refresh_rate=args.speed)
    main_w.setResizeMode(QQuickView.SizeRootObjectToView)
    main_w.show()
    sys.exit(app.exec_())

def get_eths():
    f = open("/proc/net/dev")
    data = f.read()
    f.close()
    data = data.split("\n")[2:]
    ifaces = []
    for i in data:
        if len(i.strip()) > 0:
            x = i.split()
            iface_name = x[0][:len( x[0])-1]
            ifaces.append(iface_name)
    return ifaces

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Display traffic for selected ethernet interace")
    arguments = {
        "--unit": ["units: kbps, mbps", "kbps", str],
        "--max": ["max range to display", 45, int],
        "--dir": ["tx, rx", 'tx', str],
        "--title": ["title", "", str],
        "--speed": ["sets refresh rate f = 1/refresh_rate", 10, int]
    }
    usage = ''
    for k in arguments:
        usage += "{}: {}\n".format(k, arguments[k])
        arg_parser.add_argument(k, help=arguments[k][0], default=arguments[k][1], type=arguments[k][2])
    arg_parser.add_argument("--eth", help="eth name to measure", required = True, type=str)
    arg_parser.usage = usage
    args = arg_parser.parse_args()
    eths = get_eths()
    if args.unit not in ["kbps", "mbps"]:
        print("ivalid unit {}".format(args.unit))
        sys.exit()
    if args.eth in eths:
        start_main_gui(args)
    else:
        eth_list = "   {}\n"*len(eths)
        eth_list = eth_list.format(*eths)
        print("No such eth {}".format(args.eth))
        print("Valid eth interfaces:\n{}".format(eth_list))