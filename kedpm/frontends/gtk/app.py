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
# $Id: app.py,v 1.1 2003/08/22 21:53:35 kedder Exp $

''' Gtk Frontend Application class '''


import pygtk
pygtk.require("2.0");

import gtk
import gtk.glade
import sys

from gtk import RESPONSE_OK

#print dir(gtk)

class Application:
    def __init__(self):
        #self.widgetTree = gtk.glade.XML("glade/kedpm.glade")
        pass

    def openDatabase(self):
        dlg_login = gtk.glade.XML("glade/kedpm.glade", 'dlg_login')
        dlg = dlg_login.get_widget('dlg_login')
        password = dlg_login.get_widget('password')
        res = dlg.run()
        if res == gtk.RESPONSE_OK:
            print "res is %s" % res
            print "password is", password.get_text()
        else:
            print "Good bye."
            sys.exit(1)
            
    def run(self):
        self.openDatabase()
        #gtk.main()
        pass
        
