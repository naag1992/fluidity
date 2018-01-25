#!/usr/bin/python

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""
GUI creation utilities
"""

import os
import unittest

import fluidity.diagnostics.debug as debug
import fluidity.diagnostics.utils as utils


def GuiDisabledByEnvironment():
    return "DIAGNOSTICS_GUI_DISABLED" in os.environ and \
        os.environ["DIAGNOSTICS_GUI_DISABLED"]


if not GuiDisabledByEnvironment():
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
    except ImportError:
        debug.deprint("Warning: Failed to import modules from gi repository")


def DisplayWindow(window):
    """
    Launch the GTK main loop to display the supplied window
    """

    window.connect("delete-event", Gtk.main_quit)
    window.show_all()
    Gtk.main()

    return


def DisplayWidget(widget, width=1280, height=720, title=None):
    """
    Pack the supplied widget in a simple window, and launch the GTK main loop
    to display it
    """

    window = WindowWidget(widget, width, height, title)
    DisplayWindow(window)

    return


def DisplayPlot(plot, withToolbar=True, width=1280, height=720, title=None):
    """
    Generate a widget from the supplied plot, pack the supplied widget in a
    simple window, and launch the GTK main loop to display it
    """

    widget = plot.Widget(withToolbar=withToolbar)
    widget.show_all()
    DisplayWidget(widget)

    return


def WindowWidget(widget, width=1280, height=720, title=None):
    """
    Pack the supplied widget in a simple window
    """

    window = Gtk.Window()
    window.set_default_size(width, height)
    if title is not None:
        window.set_title(title)

    window.add(widget)

    return window


def ComboBoxFromEntries(entries):
    """
    Contruct a combo box from the list of entries
    """

    comboBox = Gtk.ComboBoxText()
    for entry in entries:
        comboBox.append_text(entry)

    return comboBox


def TableFromWidgetsArray(widgets, homogeneous=False):
    """
    Construct a table containing the supplied array of widgets
    (which can be ragged)
    """

    rows, columns = len(widgets), 0
    if rows > 0:
        if utils.CanLen(widgets[0]) and not isinstance(widgets[0], Gtk.Widget):
            columns = len(widgets[0])
            for subWidget in widgets[1:]:
                columns = max(columns, len(widgets))
        else:
            widgets = [[widget] for widget in widgets]
            columns = 1

    table = Gtk.Table(rows=rows, columns=columns, homogeneous=homogeneous)

    for i in range(rows):
        for j in range(len(widgets[i])):
            table.attach(widgets[i][j], j, j + 1, i, i + 1)

    return table


class guiUnittests(unittest.TestCase):
    def testGtkSupport(self):
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk

        return

    def testComboBoxFromEntries(self):
        self.assertTrue(isinstance(ComboBoxFromEntries([]), Gtk.ComboBox))

        return
