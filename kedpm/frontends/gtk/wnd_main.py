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
# $Id: wnd_main.py,v 1.4 2003/08/26 21:33:57 kedder Exp $

'''Main KedPM window'''

import gtk
from gtk import gdk
import gobject
import globals

from kedpm.password import TYPE_STRING

from base import Window
from dialogs import AboutDialog


class MainWindow(Window):
    '''Main window of Ked Password Manager'''
    
    name = "wnd_main"

    passwords = [] # List of passwords currently displaying in the password pane
    prot = None # Prototype password instance
    password_menu = None # Popup menu for RMB in password pane
    selected_text = '' # Current selection
    

    def __init__(self):
        super(MainWindow, self).__init__()
        self.pdb = globals.app.pdb
        self.password_tree = globals.app.pdb.getTree()
        self.setupCategories()
        #self.setupPasswords()
        self.window.selection_add_target("PRIMARY", "STRING", 1)
        self.window.selection_add_target("CLIPBOARD", "STRING", 1)

    def setupCategories(self):
        category_tree = self['category_tree']
        renderer_cat = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Category', renderer_cat)
        col.add_attribute(renderer_cat, 'text', 0)
        category_tree.append_column(col)
        
        store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        root_cat = store.append(None)
        store.set(root_cat, 0, 'Root', 1, '/')
        for cat_name in self.password_tree.getBranches():
            store.set(store.append(root_cat), 0, cat_name, 1, '/'+cat_name)
            
        category_tree.set_model(store)
        category_tree.expand_all()

    def setupPasswords(self):
        password_list = self['password_list']

        # first, clear all columns in TreeView
        for column in password_list.get_columns():
            password_list.remove_column(column)
        
        self.prot = self.passwords[0]
        fields = self.prot.getFieldsOfType([TYPE_STRING])
        count = 1
        for field in fields:
            renderer = gtk.CellRendererText()
            col = gtk.TreeViewColumn(self.prot.getFieldTitle(field), renderer)
            col.add_attribute(renderer, 'text', count)
            password_list.append_column(col)
            count += 1

        store = apply(gtk.ListStore,  [gobject.TYPE_INT] + [gobject.TYPE_STRING] * count)
        
        pidx = 0
        for pwd in self.passwords:
            iter = store.append()
            store.set(iter, 0, pidx)
            pidx += 1
            count = 1
            for field in fields:
                store.set(iter, count, pwd[field])
                count += 1
        password_list.set_model(store)

    def generatePasswordPopup(self):
        menu_password = self.getGladeWidget('menu_password')
        print menu_password
        fields = self.prot.getFieldsOfType()
        fields.reverse()
        for field in fields:
            copy_mi = gtk.MenuItem('Copy %s' % self.prot.getFieldTitle(field))
            copy_mi.connect('activate', self.on_password_popup_activate, field)
            menu_password.prepend(copy_mi)
        menu_password.show_all()
        return menu_password

    def setXSelection(self, text):
        print "Copying %s" % text
        have_selection = self.window.selection_owner_set('PRIMARY')
        have_selection = self.window.selection_owner_set('CLIPBOARD')
        self.selected_text = text


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

    def on_category_tree_cursor_changed(self, data):
        category_tree = self['category_tree']
        store =  category_tree.get_model()
        path, column = category_tree.get_cursor()#path, column)

        cur_iter = store.get_iter(path)
        pass_path = store.get_value(store.get_iter(path), 1)
        tree = self.password_tree.getTreeFromPath(pass_path.split('/'))
        self.passwords = tree.getNodes()
        self.setupPasswords()

    def on_password_list_button_press_event(self, widget, event):
        if event.button == 3:
            # RMB clicked
            path, column, cell_x, cell_y = self['password_list'].get_path_at_pos(int(event.x), int(event.y))
            if not self.password_menu:
                self.password_menu = self.generatePasswordPopup()
            self.password_menu.popup(None, None, None, event.button, event.time)
            print path
        return gtk.FALSE

    def on_password_popup_activate(self, widget, data):
        print "Data is %s" % data
        store, iter = self['password_list'].get_selection().get_selected()
        password = self.passwords[store.get_value(iter, 0)]
        copytext = password[data]
        self.setXSelection(copytext)

    def on_wnd_main_selection_clear_event(self, widget, event):
        print "clearing %s selection" % event.selection

    def on_wnd_main_selection_get(self, widget, selection_data, info, time_stamp):
        print "providing selection %s" % selection_data.selection
        selection_data.set_text(self.selected_text, len(self.selected_text))
