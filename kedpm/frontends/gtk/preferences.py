# Copyright (C) 2003  Andrey Lebedev <andrey@micro.lt>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# $Id: preferences.py,v 1.1 2003/10/13 21:09:40 kedder Exp $

"""Preferences for GTK2 GUI"""
import gtk

import globals
from base import Dialog

from kedpm.config import SelectOption

class Preference(object):
    """Base class for GUI preferences items"""
    def __init__(self, option, widget):
        """option parameter is a kedpm.config.Option instance"""
        self._option = option
        self._widget = widget

    def setWidget(self):
        """Set widget to the value of option"""
        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self._widget, self._option.doc)

    def setOption(self):
        """Set option from widget value"""
        pass

class SelectPreference(Preference):
    """Preference for selection option"""
    
    def setWidget(self):
        """Build gtk menu and set the right value"""
        super(SelectPreference, self).setWidget()
        # build option menu
        menu = gtk.Menu()
        constraint = self._option.getConstraint()
        for val in constraint:
            menu.append(gtk.MenuItem(val))
        menu.show_all()
        self._widget.set_menu(menu)
        
        # set the value
        index = constraint.index(self._option.get())
        self._widget.set_history(index)

    def setOption(self):
        index = self._widget.get_history()
        value = self._option.getConstraint()[index]
        self._option.set(value)

class PreferencesDialog(Dialog):
    name="dlg_preferences"

    preferences = []
    
    def run(self):
        self.options = globals.app.conf.options
        self.setUp()
        res = self.window.run()
        self.setOptions()
        self.saveConfig()
        self.destroyDialog()

    def setUp(self):
        options = globals.app.conf.options
        self.tooltips = gtk.Tooltips()
        for opt in options.keys():
            wdg = self["wdg_" + opt]
            option = options.getOption(opt)
            preference = self.getPreferenceFromOption(option, wdg)
            preference.setWidget()
            self.preferences.append(preference)

    def setOptions(self):
        """Read preferences dialog and set options"""
        for preference in self.preferences:
            preference.setOption()
    
    def getPreferenceFromOption(self, option, widget):
        """Return preference instance depending on option type"""
        if isinstance(option, SelectOption):
            return SelectPreference(option, widget)
        else:
            raise TypeError, "Unrecognized option"

    def saveConfig(self):
        pass
