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
# $Id: app.py,v 1.2 2003/08/24 09:35:10 kedder Exp $

''' Gtk Frontend Application class '''


import pygtk
pygtk.require("2.0");

import gtk
import gtk.glade
import sys

import globals
from wnd_main import MainWindow
from kedpm.plugins.pdb_figaro import PDBFigaro

class Application(object):
    pdb = None
    wnd_main = None
    
    def __init__(self):
        #self.widgetTree = gtk.glade.XML("glade/kedpm.glade")
        pass

    def openDatabase(self):
        self.pdb = PDBFigaro()
        dlg_login = gtk.glade.XML(globals.glade_file, 'dlg_login')
        dlg = dlg_login.get_widget('dlg_login')
        password = dlg_login.get_widget('password')
        res = dlg.run()
        if res == gtk.RESPONSE_OK:
            print "res is %s" % res
            print "password is", password.get_text()
        else:
            print "Good bye."
            sys.exit(1)
        dlg.destroy()
        while gtk.events_pending(): 
            gtk.main_iteration()
        self.pdb.open(password.get_text())
        print "Passwords Loaded"
            
    def run(self):
        globals.app = self
        #self.openDatabase()
        self.wnd_main = MainWindow()
        gtk.main()
        
