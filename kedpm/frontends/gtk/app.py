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
# $Id: app.py,v 1.5 2003/09/12 18:19:53 kedder Exp $

''' Gtk Frontend Application class '''


import pygtk
pygtk.require("2.0");

import gtk
import sys

from kedpm.plugins.pdb_figaro import PDBFigaro

import globals
from wnd_main import MainWindow
from dialogs import LoginDialog
from kedpm.frontends.frontend import Frontend

class Application(object, Frontend):
    pdb = None
    wnd_main = None
    
    def openDatabase(self):
        self.pdb = PDBFigaro()
        dlg = LoginDialog(pdb = self.pdb)
        password = dlg['password']
        #while 1:
        res = dlg.run()
        '''    print "returned"'''
        if res != gtk.RESPONSE_OK:
            print "Good bye."
            sys.exit(1)

    def mainLoop(self):
        globals.app = self # Make application instance available to all modules
        self.wnd_main = MainWindow()
        gtk.main()

    def showMessage(self, message):
        dialog = gtk.MessageDialog(None,
                                    gtk.DIALOG_DESTROY_WITH_PARENT,
                                    gtk.MESSAGE_INFO,
                                    gtk.BUTTONS_CLOSE,
                                    message);
        dialog.run();
        dialog.destroy();
                
    def _run(self):
        globals.app = self # Make application instance available to all modules
        self.openDatabase()
        self.wnd_main = MainWindow()
        gtk.main()
        #from dialogs import PasswordEditDialog
        #d = PasswordEditDialog()
        #d.run()
        
