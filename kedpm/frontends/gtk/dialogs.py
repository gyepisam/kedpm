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
# $Id: dialogs.py,v 1.7 2003/09/14 12:15:57 kedder Exp $

'''Dialog classes'''

import gtk

from base import Dialog, processEvents
from kedpm.exceptions import WrongPassword
from kedpm import password, __version__
import globals

class LoginDialog(Dialog):
    name = "dlg_login"
    def __init__(self, pdb):
        super(LoginDialog, self).__init__(transient_for=None)
        self.pdb = pdb

    def run(self):
        password = self['password']
        self.message = self['message']
        while 1:
            res = self.window.run()
            if res != gtk.RESPONSE_OK:
                return res
            self.message.show()
            try:
                self.pdb.open(password.get_text())
                break
            except WrongPassword:
                self.message.set_markup('<span color="red"><b>Password incorrect. Please try again</b></span>')
                password.select_region(0, len(password.get_text()))
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
        if response_id == gtk.RESPONSE_OK:
            self.destroyDialog()
        elif response_id == 1:
            CreditsDialog(transient_for=self.window).run()


from kedpm.plugins.pdb_figaro import FigaroPassword # FIXME: this should be parametrized
class PasswordEditDialog(Dialog):
    name = "dlg_edit"

    entries = {}

    def __init__(self, password):
        '''Construct password editing dialog from password spec'''
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

    def on_show_button_toggled(self, widget, entry):
        entry.set_visibility(widget.get_active())

    def on_dlg_edit_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_OK:
            print "Accepting data"
            for field, entry in self.entries.items():
                if self.password.getField(field)['type'] == password.TYPE_TEXT:
                    buffer = entry.get_buffer()
                    b_start, b_end = buffer.get_bounds()
                    value = buffer.get_text(b_start, b_end, gtk.FALSE)
                else:
                    value = entry.get_text()
                self.password[field] = value

class AddCategoryDialog(Dialog):
    name="dlg_add_category"
    category_name = ""
    
    def process(self):
        self.category_name = self['category_name'].get_text()

def errorMessageDialog(message):
    dialog = gtk.MessageDialog(globals.app.wnd_main.window,
                                  gtk.DIALOG_DESTROY_WITH_PARENT,
                                  gtk.MESSAGE_ERROR,
                                  gtk.BUTTONS_CLOSE,
                                  message);
    dialog.run();
    dialog.destroy();
