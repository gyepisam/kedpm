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
# $Id: base.py,v 1.1 2003/08/24 09:35:10 kedder Exp $

import gtk
import globals

class Window(object):
    '''Base class for all KedPM windows.
    
    methods, which names starts with "on_" gets automatically connected to
    respective glade signals.'''
    
    name = ""
    window = None

    def __init__(self):
        self.widgetTree = gtk.glade.XML(globals.glade_file, self.name)
        # create signal table and connect
        signals = {}
        for item in dir(self):
            if item.startswith('on_'):
                print "connecting %s" % item
                signals[item] = getattr(self, item)
        self.widgetTree.signal_autoconnect(signals)
        self.window = self.widgetTree.get_widget(self.name)

class Dialog(Window):
    def __init__(self, transient_for=None):
        super(Dialog, self).__init__()
        #Window.__init__(self)
        transient_for = transient_for or globals.app.wnd_main.window
        self.window.set_transient_for(transient_for)

    def run(self):
        response = self.window.run()
        self.destroyDialog()
        return response

    def destroyDialog(self):
        self.window.destroy()

