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
# $Id: dialogs.py,v 1.1 2003/08/24 09:35:10 kedder Exp $

'''Dialog classes'''

import gtk

from base import Dialog

class CreditsDialog(Dialog):
    name = "dlg_credits"

class AboutDialog(Dialog):
    name = "dlg_about"

    def run(self):
        self.window.show()
        
    def on_dlg_about_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_OK:
            self.destroyDialog()
        elif response_id == 1:
            CreditsDialog(transient_for=self.window).run()

