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
# $Id: passdb.py,v 1.4 2004/01/04 17:07:16 kedder Exp $

""" Password Database """

from password_tree import PasswordTree

class DatabaseNotExist(IOError):
    pass

class PasswordDatabase:
    """ Base class for password databases.
    Real databases should be implemented in plugins
    """

    def __init__(self, **args):
        self._pass_tree = PasswordTree()

    def open(self, password = ""):
        """ Open database from external source """
        pass

    def save(self, fname=""):
        """ Save database to external source """
        pass

    def create(self, password, fname=""):
        """Create new password database"""
        pass

    def getTree(self):
        return self._pass_tree
