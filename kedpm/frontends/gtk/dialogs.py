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
# $Id: dialogs.py,v 1.19 2004/02/19 21:51:40 kedder Exp $

'''Dialog classes'''

import gtk
import gobject
from gtk import keysyms

from base import Dialog, processEvents
from kedpm.exceptions import WrongPassword
from kedpm.parser import parseMessage
from kedpm import password, __version__
import globals

class NewDatabaseDialog(Dialog):
    name = "dlg_new_database"
    def __init__(self):
        super(NewDatabaseDialog, self).__init__(transient_for=None)

    def run(self):
        """Return new selected password. None if Cancel button pressed."""
        while 1:
            res = self.window.run()
            if res != gtk.RESPONSE_OK:
                return None
            self['message'].show()
            if self['password'].get_text() != self['repeat'].get_text():
                self['message'].set_markup('<span color="red"><b>Passwords don\'t match. Please try again.</b></span>')
            elif self['password'].get_text() == "":
                self['message'].set_markup('<span color="red"><b>Password should not be empty.</b></span>')
            else:
                newpass = self['password'].get_text()
                self.destroyDialog()
                return newpass
            
            
class LoginDialog(Dialog):
    name = "dlg_login"
    def __init__(self, pdb):
        super(LoginDialog, self).__init__(transient_for=None)
        self.pdb = pdb

    def run(self):
        password = self['password']
        self.message = self['message']
        while 1:
            try:
                self.pdb.open(password.get_text())
                break
            except WrongPassword:
                self.message.set_markup('<span color="red"><b>Password incorrect. Please try again</b></span>')
                password.select_region(0, len(password.get_text()))
            res = self.window.run()
            if res != gtk.RESPONSE_OK:
                return res
            self.message.show()
        self.destroyDialog()
        return res

    def on_dlg_login_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_OK:
            self.message.show()
            self.message.set_markup('<b>Opening...</b>')
            processEvents()


class CreditsDialog(Dialog):
    name = "dlg_credits"

class AboutDialog(Dialog):
    name = "dlg_about"

    def __init__(self):
        super(AboutDialog, self).__init__()
        self['kedpm-version'].set_markup(self['kedpm-version'].get_label() % __version__)

    def run(self):
        self.window.show()
        
    def on_dlg_about_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_CANCEL:
            self.destroyDialog()
        elif response_id == 1:
            CreditsDialog(transient_for=self.window).run()

 # FIXME: this should be parametrized
from kedpm.plugins.pdb_figaro import FigaroPassword, FigaroPasswordTooLongError
class PasswordEditDialog(Dialog):
    name = "dlg_edit"

    entries = {}

    def __init__(self, password):
        '''Construct password editing dialog from password spec. Accept password object'''
        super(PasswordEditDialog, self).__init__()
        #self.window.hide()
        tbl = self['edit_table']

        #self.password = FigaroPassword(title="Title", notes="Notes", password="Pass")
        self.password = password
        fti = self.password.fields_type_info
        tbl.set_property('n-rows', len(fti))
        row = 0
        self.entries = {}
        for field, type_info in fti:
            label = gtk.Label(type_info['title']+":")
            label.set_alignment(0, 0)
            widget, entry = self.getEntryWidget(type_info['type'], self.password[field])
            self.entries[field] = entry
            tbl.attach(label, 0, 1, row, row+1, gtk.FILL, gtk.FILL, 0, 0)
            tbl.attach(widget, 1, 2, row, row+1, gtk.EXPAND | gtk.FILL, gtk.EXPAND, 0, 0)
            row += 1
        #tbl.show_all()
        self.window.show_all()

    def getEntryWidget(self, type, value):
        '''Return compound widget, text entry'''
        if type == password.TYPE_PASSWORD:
            entry = gtk.Entry()
            entry.set_text(value)
            hbox = gtk.HBox()
            hbox.set_spacing(6)
            entry.set_visibility(gtk.FALSE)
            hbox.pack_start(entry, gtk.FALSE, gtk.TRUE)
            btn = gtk.ToggleButton('_Show')
            btn.set_property('can-focus', gtk.FALSE)
            btn.connect('toggled', self.on_show_button_toggled, entry)
            hbox.pack_start(btn, gtk.FALSE, gtk.TRUE)
            return hbox, entry
        elif type == password.TYPE_TEXT:
            frame = gtk.Frame()
            frame.set_shadow_type(gtk.SHADOW_IN)
            scroll = gtk.ScrolledWindow()
            scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            entry = gtk.TextView()
            entry.set_wrap_mode(gtk.WRAP_WORD)
            entry.get_buffer().set_text(value)
            scroll.add(entry)
            frame.add(scroll)
            return frame, entry
        else:
            entry = gtk.Entry()
            entry.set_text(value)
            return entry, entry

    def run(self):
        password = self['password']
        self.message = self['message']
        while 1:
            res = self.window.run()
            if res != gtk.RESPONSE_OK:
                break
            if self.process():
                break
        self.destroyDialog()
        return res


    def on_show_button_toggled(self, widget, entry):
        entry.set_visibility(widget.get_active())

    #def on_dlg_edit_response(self, widget, response_id):
    def process(self):
        """Fill password object with entered data"""
        if True:
        #if response_id == gtk.RESPONSE_OK:
            props = {}
            for field, entry in self.entries.items():
                if self.password.getField(field)['type'] == password.TYPE_TEXT:
                    buf = entry.get_buffer()
                    b_start, b_end = buf.get_bounds()
                    value = buf.get_text(b_start, b_end, gtk.FALSE)
                else:
                    value = entry.get_text()
                props[field] = value
            try:
                self.password.update(props)
            except FigaroPasswordTooLongError:
                allow_save = self.askToSaveLongPass()
                if allow_save:
                    self.password.store_long_password = 1
                    self.password.update(props)
                else:
                    return False
        return True

    def askToSaveLongPass(self):
        """Return boolean user answer"""

        message = "<b>Your password is too long for Figaro Password Manager.</b>\n\n"
        message += "Figaro Password Manager can handle only passwords shorter than 24 characters.\n\n"
        message += "However, KedPM can store this password for you, but this "
        message += "will break fpm compatibility. fpm will not be able to handle such "
        message += "long password correctly.\n\n"
        message += "Do you still want to save your password?"
        
        dialog = gtk.MessageDialog(self.window,
                          gtk.DIALOG_DESTROY_WITH_PARENT,
                          gtk.MESSAGE_QUESTION,
                          gtk.BUTTONS_YES_NO,
                          ""
        );
        dialog.label.set_markup(message)
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_YES:
            return True
        return False


class AddCategoryDialog(Dialog):
    name="dlg_add_category"
    category_name = ""
    
    def process(self):
        self.category_name = self['category_name'].get_text()

class ParsePasswordDialog(Dialog):
    name="dlg_parse"
    parseddict = {}
    
    def process(self):
        patterns = globals.app.conf.patterns
        buf = self['text'].get_buffer()
        b_start, b_end = buf.get_bounds()
        text = buf.get_text(b_start, b_end, gtk.FALSE)
        self.parseddict = parseMessage(text, patterns)

class AsPlainTextDialog(Dialog):
    name="dlg_as_plain_text"
    
    def showPassword(self, pswd):
        buf = self['text'].get_buffer()
        buf.set_text(pswd.asText())

class EditParserPatterns(Dialog):
    name="dlg_patterns"
    patterns = None
    editing = None

    def __init__(self):
        super(EditParserPatterns, self).__init__()
        self.patterns = globals.app.conf.patterns
        #self.patterns = ["Hello", "World"]
        self.populate()

    def populate(self):
        plist = self['patterns']
        store = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
        renderer = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Pattern', renderer)
        col.add_attribute(renderer, 'text', 0)
        plist.append_column(col)

        # Connect selection changed event
        selection = plist.get_selection()
        selection.connect('changed', self.on_patterns_selection_changed)

        count = 0
        for pattern in self.patterns:
            pat = store.append(None)
            store.set(pat, 0, pattern)
            count += 1
        plist.set_model(store)

    def process(self):
        store = self['patterns'].get_model()
        list_iter = store.get_iter_first()
        patterns = []
        while list_iter:
            val = store.get_value(list_iter, 0)
            patterns.append(val)
            list_iter = store.iter_next(list_iter)
        globals.app.conf.patterns = patterns

    def clearEntry(self):
        self['delete_pattern'].set_sensitive(False)
        self['pattern_entry'].set_text("")
        self['pattern_entry'].grab_focus()
        self['edit_pattern'].set_label(gtk.STOCK_ADD)

    def clearPatternsSelection(self):
        sel = self['patterns'].get_selection()
        sel.unselect_all()
        self.clearEntry()
        
    def on_patterns_selection_changed(self, selection):
        plist = self['patterns']
        store, cur_iter = selection.get_selected()
        pattern_entry = self['pattern_entry']
        if cur_iter is None:
            self.editing = None
            self.clearEntry()
        else:
            # Enable delete button
            self['delete_pattern'].set_sensitive(True)
            self.editing = cur_iter
            pattern = store.get_value(cur_iter, 0)
            pattern_entry.set_text(pattern)
            self['edit_pattern'].set_label(gtk.STOCK_APPLY)

    def on_edit_pattern_clicked(self, widget):
        store = self['patterns'].get_model()
        pattern = self['pattern_entry'].get_text()
        if not pattern:
            return
        if self.editing is None:
            # Add new pattern
            store.set(store.append(), 0, pattern)
            self.clearPatternsSelection()
        else:
            # Edit selected pattern
            store.set(self.editing, 0, pattern)
            self['pattern_entry'].grab_focus()

    def on_pattern_entry_changed(self, widget):
        self['edit_pattern'].set_sensitive(widget.get_text()!="")

    def on_new_pattern_clicked(self, widget):
        self.clearPatternsSelection()

    def on_delete_pattern_clicked(self, widget):
        if self.editing:
            store = self['patterns'].get_model()
            store.remove(self.editing)


def errorMessageDialog(message):
    dialog = gtk.MessageDialog(globals.app.wnd_main.window,
                                  gtk.DIALOG_DESTROY_WITH_PARENT,
                                  gtk.MESSAGE_ERROR,
                                  gtk.BUTTONS_CLOSE,
                                  message)
    dialog.run()
    dialog.destroy()
