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
# $Id: password.py,v 1.1 2003/08/05 18:32:18 kedder Exp $

""" Password item """

class Password:
    """ Basic class for password structure """
    fields = {
        "host": "Host",
        "name": "Username",
        "password": "Password",
    }

    searchable = ["host", "name"]
    listable = searchable
  
    host = ""
    name = "" 
    password ="" 

    def __init__(self, host="", name="", password=""):
        self.host = host
        self.name = name
        self.password = password    
    
    def __str__(self):
        return "Password for <%s>" % self.name

    def asText(self):
        text = """
Host:     %s
Username: %s
Password: %s
""" % (self.host, self.name, self.password)
        return text
