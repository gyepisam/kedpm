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
# $Id: base.py,v 1.6 2005/03/05 21:44:33 kedder Exp $

import gtk
import gtk.glade
import globals

def processEvents():
    while gtk.events_pending():
        gtk.main_iteration_do(gtk.FALSE)

class Window(object):
    '''Base class for all KedPM windows.
    
    methods, which names starts with "on_" gets automatically connected to
    respective glade signals.'''
    
    name = ""
    window = None
    signals = {}
    #menu_names=[]
    #menus = {}
    

    def __init__(self):
        self.widgetTree = gtk.glade.XML(globals.glade_file, self.name)
        # create signal table and connect it
        signals = {}
        for item in dir(self):
            if item.startswith('on_'):
                signals[item] = getattr(self, item)
        self.signals = signals
        self.widgetTree.signal_autoconnect(self.signals)
        self.window = self.widgetTree.get_widget(self.name)
        #for menu in self.menu_names:
        #    print "Loading", menu
        #    menu_wt = gtk.glade.XML(globals.glade_file, menu)
        #    menu_wt.signal_autoconnect(signals)
        #    self.menus[menu] = menu_wt.get_widget(menu)

    def __getitem__(self, name):
        return self.widgetTree.get_widget(name)

    def getGladeWidget(self, name):
        widgetTree = gtk.glade.XML(globals.glade_file, name)
        widgetTree.signal_autoconnect(self.signals)
        return widgetTree.get_widget(name)

class Dialog(Window):
    """Base class for modal dialogs"""
    def __init__(self, transient_for="main"):
        super(Dialog, self).__init__()
        #Window.__init__(self)
        if transient_for:
            if transient_for=="main":
                transient_for = globals.app.wnd_main.window
            self.window.set_transient_for(transient_for)

    #def run(self):
    #    """Create dialog and wait for user input. Return user response."""
    #    response = self.window.run()
    #    if response == gtk.RESPONSE_OK:
    #        self.process()
    #    self.destroyDialog()
    #    return response

    def run(self):
        """Present dialog window to the user."""
        while 1:
            resp = self.window.run()
            if resp in (gtk.RESPONSE_CANCEL, gtk.RESPONSE_DELETE_EVENT):
                self.destroyDialog()
                return resp
            
            done = self.process(resp)
            if done:
                self.destroyDialog()
                return resp

    def destroyDialog(self):
        self.window.destroy()

    def process(self, resp_id):
        """Perform any processing of entered data.
        
        Return True if data is processed successfuly, or False if data needs
        corrections. If True is returned, dialog will be destroyed.
        """
        return True
