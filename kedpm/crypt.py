# KED Password Manager
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
# $Id: crypt.py,v 1.1 2003/08/05 18:32:18 kedder Exp $

""" Cryptography algorythms for KED Password Manager
"""

class Crypt:
    """ Base class for ctypting plugins """
    def encrypt(self, data):
        """ Encrypt given data 
        """
        return data

    def decrypt(self, data):
        """ Return parameter list needed for encription
        """
        return data

    
    
