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
# $Id: app.py,v 1.7 2004/01/04 17:07:16 kedder Exp $

''' Gtk Frontend Application class '''


import pygtk
pygtk.require("2.0");

import gtk
import sys
from os.path import expanduser

from kedpm.plugins.pdb_figaro import PDBFigaro
from kedpm.passdb import DatabaseNotExist

import globals
from wnd_main import MainWindow
from dialogs import NewDatabaseDialog, LoginDialog
from kedpm.frontends.frontend import Frontend

class Application(object, Frontend):
    pdb = None
    wnd_main = None
    
    def openDatabase(self):
        self.pdb = PDBFigaro(filename = expanduser(self.conf.options['fpm-database']))
        dlg = LoginDialog(pdb = self.pdb)
        password = dlg['password']
        try:
            res = dlg.run()
            if res != gtk.RESPONSE_OK:
                print "Good bye."
                sys.exit(1)
        except DatabaseNotExist:
            dlg.destroyDialog()
            newpass = self.createNewDatabase()
            if newpass is None:
                sys.exit(1)
            self.pdb.open(newpass)

    def createNewDatabase(self):
        """Create new password database and return password for created
        database"""
        dlg = NewDatabaseDialog()
        newpass = dlg.run()
        self.pdb.create(newpass, expanduser(self.conf.options['fpm-database']))
        return newpass

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
        
