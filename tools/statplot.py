#!/usr/bin/python
#
# James Maddison
# Thomas Duvernay
# -> Port to Gtk 3.0 in order to fix a graphical artefact
# -> Use of argparse instead of deprecated getopt
# -> Miscellaneous fixes

"""
Plot data in a .stat file
"""

import argparse
import sys
import time

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import fluidity.diagnostics.fluiditytools as fluidity_tools
import fluidity.diagnostics.gui as gui
import fluidity.diagnostics.plotting as plotting

parser = argparse.ArgumentParser()
parser.add_argument('statfile', nargs=1)
args = parser.parse_args(sys.argv[1:])


class StatplotWindow(Gtk.Window):
    def __init__(self, filenames):
        self._filenames = filenames

        Gtk.Window.__init__(self)
        self.set_title(self._filenames[-1])
        self.connect("key-press-event", self._KeyPressed)

        self._ReadData()

        # Containers
        self._vBox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self._vBox)

        self._hBox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self._vBox.pack_end(self._hBox, False, False, 0)

        # The plot widget
        self._xField = None
        self._yField = None
        self._xData = None
        self._yData = None
        self._plotWidget = None
        self._plotType = plotting.LinePlot

        # The combos
        paths = sorted(self._stat.Paths())
        self._xCombo = gui.ComboBoxFromEntries(paths)
        self._xCombo.connect("changed", self._XComboChanged)
        if "ElapsedTime" in paths:
            iter1 = self._xCombo.get_model(). \
                get_iter("%d" % paths.index("ElapsedTime"))
        else:
            iter1 = self._xCombo.get_model().get_iter_first()
        if iter1 is not None:
            self._xCombo.set_active_iter(iter1)
        self._hBox.pack_start(self._xCombo, True, True, 0)

        self._yCombo = gui.ComboBoxFromEntries(paths)
        self._yCombo.connect("changed", self._YComboChanged)
        iter1 = self._yCombo.get_model().get_iter_first()
        if iter1 is not None:
            iter2 = self._yCombo.get_model().iter_next(iter1)
            if iter2 is None:
                self._yCombo.set_active_iter(iter1)
            else:
                self._yCombo.set_active_iter(iter2)
            self._hBox.pack_end(self._yCombo, True, True, 0)

        self._vBox.show_all()

        return

    def _ReadData(self):
        stats = []
        for i, filename in enumerate(self._filenames):
            failcount = 0
            while failcount < 5:
                try:
                    stats.append(fluidity_tools.Stat(filename))
                    break
                except TypeError, ValueError:
                    # We opened the .stat when it was being written to by
                    # fluidity
                    time.sleep(0.2)
                    failcount = failcount + 1
            if failcount == 5:
                raise Exception("Could not open %s" % filename)
        if len(stats) == 1:
            self._stat = stats[0]
        else:
            self._stat = fluidity_tools.JoinStat(*stats)

        return

    def _RefreshData(self, keepBounds=False):
        self._xField = self._xCombo.get_active_text()
        self._xData = self._stat[self._xField]
        self._yField = self._yCombo.get_active_text()
        self._yData = self._stat[self._yField]
        if keepBounds:
            axis = self._plotWidget.get_children()[0].figure.get_axes()[0]
            bounds = (axis.get_xbound(), axis.get_ybound())
        else:
            bounds = None
        self._RefreshPlot(bounds)

        return

    def _RefreshPlot(self, bounds=None, xscale=None, yscale=None):
        if self._xData is not None and self._yData is not None:
            assert(len(self._xData) == len(self._yData))
            if self._plotWidget is not None:
                self._vBox.remove(self._plotWidget)
                axis = self._plotWidget.get_children()[0].figure.get_axes()[0]
                if xscale is None:
                    xscale = axis.get_xscale()
                if yscale is None:
                    yscale = axis.get_yscale()
            else:
                if xscale is None:
                    xscale = "linear"
                if yscale is None:
                    yscale = "linear"

            self._plotWidget = self._plotType(x=self._xData, y=self._yData,
                                              xLabel=self._xField,
                                              yLabel=self._yField).Widget()
            axis = self._plotWidget.get_children()[0].figure.get_axes()[0]
            axis.set_xscale(xscale)
            axis.set_yscale(yscale)
            if bounds is not None:
                axis.set_xbound(bounds[0])
                axis.set_ybound(bounds[1])

            self._vBox.pack_start(self._plotWidget, True, True, 0)
            self._plotWidget.show_all()
            window.show_all()
            Gtk.main()

        return

    def SetXField(self, field):
        self._xField = field
        self._xData = self._stat[self._xField]

        self._RefreshPlot()

        return

    def SetYField(self, field):
        self._yField = field
        self._yData = self._stat[self._yField]

        self._RefreshPlot()

        return

    def _XComboChanged(self, widget):
        self.SetXField(self._xCombo.get_active_text())

        return

    def _YComboChanged(self, widget):
        self.SetYField(self._yCombo.get_active_text())

        return

    def _KeyPressed(self, widget, event):
        char = event.string
        if char == "R":
            self._ReadData()
            self._RefreshData(keepBounds=True)
        elif char == "l":
            self._plotType = plotting.LinePlot
            self._RefreshData(keepBounds=True)
        elif char == "x":
            scale = self._plotWidget.get_children()[0].figure.get_axes()[0]. \
                get_xscale()
            if scale == "linear":
                self._RefreshPlot(xscale="log")
            else:
                self._RefreshPlot(xscale="linear")
        elif char == "y":
            scale = self._plotWidget.get_children()[0].figure.get_axes()[0]. \
                get_yscale()
            if scale == "linear":
                self._RefreshPlot(yscale="log")
            else:
                self._RefreshPlot(yscale="linear")
        elif char == "q":
            self.destroy()
        elif char == "r":
            self._ReadData()
            self._RefreshData()
        elif char == "s":
            self._plotType = plotting.ScatterPlot
            self._RefreshData(keepBounds=True)

        return


# The window
window = StatplotWindow(args.statfile)
window.set_default_size(1280, 720)
window.set_position(Gtk.WindowPosition.CENTER)

# Fire up the GUI
gui.DisplayWindow(window)
