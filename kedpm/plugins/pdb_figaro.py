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
# $Id: pdb_figaro.py,v 1.4 2003/08/11 20:14:30 kedder Exp $

""" Figaro password manager database plugin """

import os

from xml.dom import minidom
from string import strip
from Crypto.Cipher import Blowfish
from Crypto.Hash import MD5

from kedpm.exceptions import WrongPassword
from kedpm.passdb import PasswordDatabase
from kedpm.password_tree import PasswordTree
from kedpm.password import Password, TYPE_STRING, TYPE_TEXT, TYPE_PASSWORD

class FigaroPassword (Password):
    fields_type_info = [
        ('title',     {'title': 'Title', 'type': TYPE_STRING}),
        ('user',     {'title': 'Username', 'type': TYPE_STRING}),
        ('url',     {'title': 'URL', 'type': TYPE_STRING}),
        ('notes',     {'title': 'Notes', 'type': TYPE_TEXT}),
        ('password', {'title': 'Password', 'type': TYPE_PASSWORD}),
    ]

class PDBFigaro (PasswordDatabase):

    default_db_filename = os.getenv('HOME') + '/.fpm/fpm'

    def open(self, password, fname=""):
        ''' Open figaro password database and construct password tree '''
        self._password = password
        fpm = minidom.parse(fname or self.default_db_filename)
        keyinfo = fpm.documentElement.getElementsByTagName("KeyInfo")[0]
        self._salt = keyinfo.getAttribute('salt')
        vstring = keyinfo.getAttribute('vstring')
        if self.decrypt(vstring) != "FIGARO":
           raise WrongPassword, "Wrong password"
       
        nodes = fpm.documentElement.getElementsByTagName("PasswordItem")
        for node in nodes:
            category = self._getTagData(node, "category")
            branch = self._pass_tree.get(category)
            if not branch:
                branch = self._pass_tree.addBranch(category)
            branch.addNode(self._getPasswordFromNode(node))
    
    def _getPasswordFromNode(self, node):
        ''' Create password instance from given fpm node '''
        fields = ["title", "user", "url", "notes", "password"]
        params = {}
        for field in fields:
            params[field] = self._getTagData(node, field)
        return FigaroPassword(**params)
    
    def _getTagData(self, node, tag):
        chnode = node.getElementsByTagName(tag)
        if chnode and node.hasChildNodes():
            datanode= chnode.pop()
            encrypted = ""
            # datanode can have more than one text chunk
            for child in datanode.childNodes:
                encrypted += child.data
            assert len(encrypted) % 8 == 0
            return self.decrypt(encrypted)
        else: return ""    
    
    def decrypt(self, string):
        ''' Decrypt FPM encoded string '''        
        hash=MD5.new()
        hash.update(self._salt + self._password)
        key = hash.digest()
        bf = Blowfish.new(key)
        hexstr = self._hex_to_bin(string)
        rotated = bf.decrypt(hexstr)
        plaintext = self._unrotate(rotated)
        return plaintext

    def _hex_to_bin(self, strin):
        strout = ""
        for i in range(len(strin) / 2):
            high = ord(strin[i * 2]) - ord('a')
            low = ord(strin[i * 2 + 1]) - ord('a')
            data = high * 16 + low
            assert data < 256
            strout = strout + chr(data)
        return strout

    def _unrotate(self, field):
        plaintext = ""
        tmp = {}
        blocksize = Blowfish.block_size
        num_blocks = len(field)/blocksize
        for b in range(num_blocks):
            for i in range(blocksize):
                tmp[i*num_blocks+b] = field[b*blocksize+i]

        for c in range(len(tmp)):
            if tmp[c] == chr(0):
                break
            plaintext = plaintext + tmp[c]
        return str(plaintext)


