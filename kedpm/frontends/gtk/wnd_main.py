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
# $Id: wnd_main.py,v 1.28 2004/02/28 18:45:20 kedder Exp $

'''Main KedPM window'''
import os
import gtk
from gtk import gdk
import gobject
import globals

from kedpm.password import TYPE_STRING
from kedpm.exceptions import RenameError

from base import Window, processEvents
import dialogs
from preferences import PreferencesDialog
from dialogs import errorMessageDialog
from kedpm.plugins.pdb_figaro import FigaroPassword # FIXME: this should be parametrized

class MainWindow(Window):
    '''Main window of Ked Password Manager'''

    name = "wnd_main"
    #menu_names = ['menu_category']
    menu_category = None
    menu_password = None

    modified = False        # Is database modified?
    passwords = []          # List of passwords currently displaying in the password pane
    prot = None             # Prototype password instance
    password_menu = None    # Popup menu for RMB in password pane
    selected_text = ''      # Current selection
    cwtree = None           # Current working tree
    search_text = ''        # Current password filter
    flat_view = False       # Is password list flat?
    search_history = []     # List of searched strings
    search_history_file = os.getenv("HOME") + '/.kedpm/gui_search_history'



    def __init__(self):
        super(MainWindow, self).__init__()
        self.pdb = globals.app.pdb
        self.cwtree = self.password_tree = globals.app.pdb.getTree()
        self.setupCategories()
        self.setupPasswords()
        pl_selection = self["password_list"].get_selection()
        pl_selection.connect("changed", self.on_password_list_selection_changed)

        self['category_tree'].grab_focus()
        self.window.selection_add_target("PRIMARY", "STRING", 1)
        self.window.selection_add_target("CLIPBOARD", "STRING", 1)
        self.menu_category = self.getGladeWidget('menu_category')
        #self.menu_password = self.getGladeWidget('menu_password')

        # Other widgets setup
        self.statusbar = self['statusbar']
        self.setModified(False)

        #import pdb; pdb.set_trace()
        self['search_combo'].disable_activate()
        self.loadHistory()

    def setupCategories(self):
        category_tree = self['category_tree']
        renderer_cat = gtk.CellRendererText()
        renderer_cat.set_property("editable", True)
        renderer_cat.connect('edited', self.on_category_edited)
        col = gtk.TreeViewColumn('Category', renderer_cat)
        col.add_attribute(renderer_cat, 'text', 0)
        category_tree.append_column(col)

        self.updateCategories()

    def updateCategories(self):
        category_tree = self['category_tree']
        store = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        root_cat = store.append(None)
        store.set(root_cat, 0, 'Root', 1, '/')
        self.buildCategoryTree(store, root_cat, self.password_tree, '/')
        #for cat_name in self.password_tree.getBranches():
        #    store.set(store.append(root_cat), 0, cat_name, 1, '/'+cat_name)
        category_tree.set_model(store)
        category_tree.expand_all()

    def buildCategoryTree(self, store, root_iter, tree_branch, path):
        for cat_name in tree_branch.getBranches():
            sub_iter = store.append(root_iter)
            store.set(sub_iter, 0, cat_name, 1, path+cat_name+'/')
            if tree_branch[cat_name].getBranches():
                self.buildCategoryTree(store, sub_iter, tree_branch[cat_name], path+cat_name+'/')

    def setupPasswords(self):
        """Rebuild and redraw password list.

        This function should be called every time password database changed."""

        password_list = self['password_list']

        # first, clear all columns in TreeView
        for column in password_list.get_columns():
            password_list.remove_column(column)

        passwords = self.getCWTree().locate(self.search_text)

        if passwords:
            self.prot = passwords[0]
            fields = self.prot.getFieldsOfType([TYPE_STRING])
            count = 1
            for field in fields:
                renderer = gtk.CellRendererText()
                col = gtk.TreeViewColumn(self.prot.getFieldTitle(field), renderer)
                col.set_resizable(True)
                col.set_sort_column_id(count)
                col.add_attribute(renderer, 'text', count)
                password_list.append_column(col)
                count += 1

            store = apply(gtk.ListStore,  [gobject.TYPE_INT] + [gobject.TYPE_STRING] * count)

            pidx = 0
            for pwd in passwords:
                iter = store.append()
                store.set(iter, 0, pidx)
                pidx += 1
                count = 1
                for field in fields:
                    store.set(iter, count, pwd[field])
                    count += 1
        else:
            store = gtk.ListStore(gobject.TYPE_STRING)
        self.passwords = passwords
        password_list.set_model(store)
        self.updateControls()

    def getCWTree(self):
        if self.flat_view:
            return self.password_tree.flatten()
        else:
            return self.cwtree

    def updateControls(self):
        """Update controls according to current status.

        Set the sensitive property of widgets, that are meaningless in current
        program state"""

        # Check if any password is currently selected
        pwd_controls = ["tb_edit", "tb_delete", "mi_edit_password",
            "mi_delete_password", "mi_as_plain_text"]
        pwd_sensitive = False
        if self.getSelectedPassword():
            pwd_sensitive = True
        for control in pwd_controls:
            self[control].set_sensitive(pwd_sensitive)
        # Disable "Clear" button if search entry is empty
        search_text = self['search_entry'].get_text()
        #clear_sensitive = False
        #if search_text:
        #    clear_sensitive = True
        self["clear_button"].set_sensitive(search_text and True or False)

    def generatePasswordPopup(self):
        #menu_password = self.menu_password
        menu_password = self.getGladeWidget('menu_password')
        fields = self.prot.getFieldsOfType()
        fields.reverse()
        for field in fields:
            copy_mi = gtk.MenuItem('Copy %s' % self.prot.getFieldTitle(field))
            copy_mi.connect('activate', self.on_password_popup_activate, field)
            menu_password.prepend(copy_mi)
        menu_password.show_all()
        return menu_password

    def setXSelection(self, text):
        have_selection = self.window.selection_owner_set('PRIMARY')
        have_selection = self.window.selection_owner_set('CLIPBOARD')
        self.selected_text = text

    def getSelectedPassword(self):
        store, iter = self['password_list'].get_selection().get_selected()
        if iter:
            password = self.passwords[store.get_value(iter, 0)]
            return password
        else:
            return None

    def setModified(self, modified):
        """Set modified flag and update related widgets"""
        self.modified = modified
        self["tb_save"].set_sensitive(modified)
        self["mi_save"].set_sensitive(modified)

    def tryToSave(self):
        self.setModified(True)
        savemode = globals.app.conf.options["save-mode"]
        response = gtk.RESPONSE_YES
        if savemode == 'no':
            response = gtk.RESPONSE_NO
        if savemode == 'ask':
            dialog = gtk.MessageDialog(self.window,
                                      gtk.DIALOG_DESTROY_WITH_PARENT,
                                      gtk.MESSAGE_QUESTION,
                                      gtk.BUTTONS_YES_NO,
                                      "Password database has changed.\nDo you want to save it now?");
            response = dialog.run();
            dialog.destroy();
        if response == gtk.RESPONSE_YES:
            self.doSaveDatabase()

    def doSaveDatabase(self):
        """Actually save password database and display indication in statusbar"""
        cid = self.statusbar.get_context_id('toolbar')
        self.pdb.save()
        self.statusbar.pop(cid)
        self.statusbar.push(cid, "Password database saved.")
        self.setModified(False)

    def addPasswordInteractively(self, pswd = None):
        """Add the given password to the current category interactively. 
        
        Let user deside add the password or not and let him correct information
        before adding."""
        
        if pswd is None:
            pswd = FigaroPassword()
        dlg = dialogs.PasswordEditDialog(pswd)
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            self.getCWTree().addNode(pswd)
            self.setupPasswords()
            self.tryToSave()

    def toggleFlatView(self):
        """Toggle flat password view and update related controls"""
        self.flat_view = not self.flat_view
        self['scroll_tree'].set_property("visible", not self.flat_view)
        self['tb_flat_tree'].set_active(self.flat_view)
        self['mi_flat_tree'].set_active(self.flat_view)
        # disable some controls
        for control in ['tb_add', 'mi_add_password', 'mi_parse_password']:
            self[control].set_sensitive(not self.flat_view)
        if self.flat_view:
            # put focus on search entry
            self['search_entry'].grab_focus()
        self.setupPasswords()

    def updateHistory(self):
        """Update history with string in search_entry"""
        search_entry = self['search_entry']
        search_text = search_entry.get_text()
        if search_text and search_text not in self.search_history:
            self.search_history.insert(0, search_text)
            self['search_combo'].set_popdown_strings(self.search_history)

    def loadHistory(self):
        if os.access(self.search_history_file, os.R_OK):
            f = open(self.search_history_file, 'r')
            hist = f.read()
            f.close()
            self.search_history = hist.split('\n')
            self['search_combo'].set_popdown_strings(self.search_history)
            self['search_entry'].set_text('')

    def saveHistory(self):
        f = open(self.search_history_file, 'w')
        f.write('\n'.join(self.search_history))
        f.close()

    def performSearch(self, update_history=True):
        """Search passwords based on filter entered to search entry.

        Update search history if needed."""
        
        search_entry = self['search_entry']
        search_text = search_entry.get_text()
        
        # Do search
        if search_text != self.search_text:
            self.search_text = search_text
            self.setupPasswords()

        # Update history list
        if update_history:
            self.updateHistory()

    #################################################################
    # Signal handlers
    def on_wnd_main_destroy(self, widget):
        if self.modified:
            self.tryToSave()
        self.saveHistory()
        print "Exiting."
        gtk.main_quit() #make the program quit

    def on_mi_quit_activate(self, widget):
        '''Menu: File->Quit'''
        self.on_wnd_main_destroy(widget)

    def on_mi_about_activate(self, widget):
        '''Menu: Help->About'''
        dlg = dialogs.AboutDialog()
        dlg.run()

    def on_category_tree_cursor_changed(self, data):
        category_tree = self['category_tree']
        store =  category_tree.get_model()
        path, column = category_tree.get_cursor()#path, column)

        cur_iter = store.get_iter(path)
        pass_path = store.get_value(cur_iter, 1)
        self.cwtree = self.password_tree.getTreeFromPath(pass_path.split('/'))
        self.setupPasswords()

    def on_password_list_button_press_event(self, widget, event):
        if event.button == 3:
            # RMB clicked
            pathinfo = self['password_list'].get_path_at_pos(int(event.x), int(event.y))
            if pathinfo:
                #path, column, cell_x, cell_y = pathinfo
                #if not self.password_menu:
                password_menu = self.generatePasswordPopup()
                password_menu.popup(None, None, None, event.button, event.time)
        return gtk.FALSE

    def on_category_tree_button_press_event(self, widget, event):
        if event.button == 3:
            self.menu_category.popup(None, None, None, event.button, event.time)
        return gtk.FALSE

    def on_password_popup_activate(self, widget, data):
        password = self.getSelectedPassword()
        copytext = password[data]
        self.setXSelection(copytext)

    def on_wnd_main_selection_clear_event(self, widget, event):
        print "clearing %s selection" % event.selection

    def on_wnd_main_selection_get(self, widget, selection_data, info, time_stamp):
        selection_data.set_text(self.selected_text, len(self.selected_text))

    def on_find_button_activate(self, widget):
        self.performSearch()

    def on_clear_button_activate(self, widget):
        self['search_entry'].set_text('')
        self.performSearch()

    def on_tb_edit_clicked(self, widget):
        sel_pswd = self.getSelectedPassword()
        if sel_pswd:
            dlg = dialogs.PasswordEditDialog(sel_pswd)
            response = dlg.run()
            if response == gtk.RESPONSE_OK:
                self.setupPasswords()
                self.tryToSave()

    def on_pmi_edit_activate(self, widget):
        '''password list popup 'Edit' item clicked'''
        self.on_tb_edit_clicked(widget)

    def on_pmi_delete_activate(self, widget):
        '''password list popup 'Delete' item clicked'''
        self.on_tb_delete_clicked(widget)

    def on_tb_add_clicked(self, widget):
        '''Toolbar 'Add' button clicked'''
        self.addPasswordInteractively()

    def on_mi_save_activate(self, widget):
        '''Main menu 'Save' item activated'''
        self.doSaveDatabase()

    def on_mi_add_category_activate(self, widget):
        '''Main menu 'Add category' item activated'''
        dlg = dialogs.AddCategoryDialog()
        response = dlg.run()
        if response == gtk.RESPONSE_OK and dlg.category_name!='':
            try:
                self.getCWTree().addBranch(dlg.category_name)
            except AttributeError:
                errorMessageDialog('Directory "%s" already exists!' % dlg.category_name);
            else:
                self.updateCategories()

    def on_category_tree_popup_menu(self, wodget):
        '''Shift-F10 pressed in category tree'''
        self.menu_category.popup(None, None, None, 0, gtk.get_current_event_time())

    def on_password_list_popup_menu(self, widget):
        '''Shift-F10 pressed in password tree'''
        password_menu = self.generatePasswordPopup()
        password_menu.popup(None, None, None, 0, gtk.get_current_event_time())

    def on_category_edited(self, renderer, path, newname):
        category_tree = self['category_tree']
        store =  category_tree.get_model()
        cur_iter = store.get_iter(path)
        cat_path = store.get_value(store.get_iter(path), 1)
        path = cat_path.split('/')
        if path[-2] != newname:
            try:
                self.password_tree.renameBranch(cat_path.split('/'), newname)
            except RenameError, message:
                errorMessageDialog(message[0])
                return
            self.updateCategories()
            self.tryToSave()

    def on_mi_preferences_activate(self, widget):
        dlg = PreferencesDialog()
        dlg.run()

    def on_search_entry_focus_in_event(self, widget, focus):
        cid = self.statusbar.get_context_id('search')
        self.statusbar.push(cid, "You can use regular expressions to search passwords.")

    def on_search_entry_focus_out_event(self, widget, focus):
        cid = self.statusbar.get_context_id('search')
        self.statusbar.pop(cid)
        self.updateHistory()

    def on_tb_delete_clicked(self, widget):
        sel_pswd = self.getSelectedPassword()
        if not sel_pswd:
            return
        # Ask user is he sure
        dialog = gtk.MessageDialog(self.window,
                                  gtk.DIALOG_DESTROY_WITH_PARENT,
                                  gtk.MESSAGE_QUESTION,
                                  gtk.BUTTONS_YES_NO,
                                  "Are you really want to delete this password?");
        response = dialog.run();
        dialog.destroy();
        if response == gtk.RESPONSE_YES:
            # Delete password
            self.password_tree.removeNode(sel_pswd)
            self.setupPasswords()
            cid = self.statusbar.get_context_id('toolbar')
            self.statusbar.pop(cid)
            self.statusbar.push(cid, "Password deleted.")
            self.tryToSave()

    def on_password_list_selection_changed(self, widget):
        self.updateControls()

    def on_mi_parse_password_activate(self, widget):
        dlg = dialogs.ParsePasswordDialog()
        response = dlg.run()
        if response == gtk.RESPONSE_OK:
            pswd = FigaroPassword()
            pswd.update(dlg.parseddict)
            self.addPasswordInteractively(pswd)

    def on_mi_as_plain_text_activate(self, widget):
        sel_pswd = self.getSelectedPassword()
        if sel_pswd:
            dlg = dialogs.AsPlainTextDialog()
            dlg.showPassword(sel_pswd)
            dlg.run()

    def on_pmi_view_as_plain_text_activate(self, widget):
        self.on_mi_as_plain_text_activate(widget)

    def on_mi_flat_tree_activate(self, widget):
        if widget.get_active() != self.flat_view:
            self.toggleFlatView()

    def on_tb_flat_tree_toggled(self, widget):
        if widget.get_active() != self.flat_view:
            self.toggleFlatView()

    def on_edit_parser_patterns_activate(self, widget):
        dlg = dialogs.EditParserPatterns()
        dlg.run()
        globals.app.conf.save()
        
    def on_search_entry_changed(self, widget):
        self.performSearch(update_history=False)
