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
# $Id: wnd_main.py,v 1.1 2003/08/24 09:35:10 kedder Exp $

'''Main KedPM window'''

import gtk
import globals

from base import Window
from dialogs import AboutDialog

class MainWindow(Window):
    '''Main window of Ked Password Manager'''
    
    name = "wnd_main"

    # Signal handlers
    def on_wnd_main_destroy(self, widget):
        print "Exiting."
        gtk.main_quit() #make the program quit

    def on_mi_quit_activate(self, widget):
        '''Menu: File->Quit'''
        
        self.on_wnd_main_destroy(widget)

    def on_mi_about_activate(self, widget):
        '''Menu: Help->About'''
        dlg = AboutDialog()
        dlg.run()

