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
# $Id: pdb_figaro.py,v 1.7 2003/08/15 20:43:22 kedder Exp $

""" Figaro password manager database plugin """

import os

from xml.dom import minidom
from string import strip
from Crypto.Cipher import Blowfish
from Crypto.Hash import MD5

from random import randint

from kedpm.exceptions import WrongPassword
from kedpm.passdb import PasswordDatabase
from kedpm.password_tree import PasswordTree
from kedpm.password import Password, TYPE_STRING, TYPE_TEXT, TYPE_PASSWORD, TYPE_META

FPM_PASSWORD_LEN = 24

class FigaroPassword (Password):
    fields_type_info = [
        ('title',     {'title': 'Title', 'type': TYPE_STRING}),
        ('user',     {'title': 'Username', 'type': TYPE_STRING}),
        ('url',     {'title': 'URL', 'type': TYPE_STRING}),
        ('notes',     {'title': 'Notes', 'type': TYPE_TEXT}),
        ('password', {'title': 'Password', 'type': TYPE_PASSWORD}),
    ]

    default = 0
    launcher = ""

    def __init__(self, **kw):
        Password.__init__(self, **kw)
        self.default = kw.get('default', 0)
        self.launcher = kw.get('launcher', '')

class PDBFigaro (PasswordDatabase):

    default_db_filename = os.getenv('HOME') + '/.fpm/fpm'
    #default_db_filename = 'test/fpm.sample'

    def open(self, password, fname=""):
        ''' Open figaro password database and construct password tree '''
        
        self._password = password
        self.filename = fname or self.default_db_filename
        fpm = minidom.parse(self.filename)
        keyinfo = fpm.documentElement.getElementsByTagName("KeyInfo")[0]
        self._salt = keyinfo.getAttribute('salt')
        vstring = keyinfo.getAttribute('vstring')
        if self.decrypt(vstring) != "FIGARO":
            raise WrongPassword, "Wrong password"

        # Save LauncherList xml element. Although kedpm don't use launchers
        # yet, this list will be inserted into saved database to preserve
        # compatibility with fpm.

        nodes = fpm.documentElement.getElementsByTagName("LauncherList")
        if nodes:
            assert len(nodes) == 1
            self.launcherlist = nodes[0]

        nodes = fpm.documentElement.getElementsByTagName("PasswordItem")
        for node in nodes:
            category = self._getTagData(node, "category")
            branch = self._pass_tree.get(category)
            if not branch:
                branch = self._pass_tree.addBranch(category)
            branch.addNode(self._getPasswordFromNode(node))

    def save(self, fname="fpm.kedpm-saved"):
        '''Save figaro password database'''
    
        doc = self.buildPasswordTree()
        f = open(fname, 'w')
        f.write(doc.toxml())
        f.close()
        

    def buildPasswordTree(self):
        '''Build and return DOM document from current password tree'''
        
        domimpl = minidom.getDOMImplementation()
        document= domimpl.createDocument("http://kedpm.sourceforge.net/xml/fpm", "FPM", None)
        root = document.documentElement
        root.setAttribute('full_version', '00.53.00')
        root.setAttribute('min_version', '00.50.00')
        root.setAttribute('display_version', '0.53')
        # KeyInfo tag
        keyinfo = document.createElement('KeyInfo')
        keyinfo.setAttribute('salt', self._salt)
        keyinfo.setAttribute('vstring', self.encrypt('FIGARO'))
        root.appendChild(keyinfo)
        
        # Add LauncherList for fpm compatibility
        root.appendChild(self.launcherlist)

        # PasswordList tag
        passwordlist = document.createElement('PasswordList')
        props = ['title', 'user', 'url', 'notes']
        iter = self._pass_tree.getIterator()
        while 1:
            pwd = iter.next()
            if pwd is None:
                break
            pwitem = document.createElement('PasswordItem')
            for prop in props:
                pr_node_text = document.createTextNode(self.encrypt(pwd[prop]))
                pr_node = document.createElement(prop)
                pr_node.appendChild(pr_node_text)
                pwitem.appendChild(pr_node)

            password = document.createElement('password')
            text = document.createTextNode(self.encrypt(pwd['password'], 1))
            password.appendChild(text)
            pwitem.appendChild(password)

            category = document.createElement('category')
            text = document.createTextNode(self.encrypt(iter.getCurrentCategory()))
            category.appendChild(text)
            pwitem.appendChild(category)

            # Following launcher and default tags for fpm compatibility
            launcher = document.createElement('launcher')
            text = document.createTextNode(self.encrypt(pwd.launcher))
            launcher.appendChild(text)
            pwitem.appendChild(launcher)

            if pwd.default:
                pwitem.appendChild(document.createElement('default'))

            passwordlist.appendChild(pwitem)
        root.appendChild(passwordlist)

        return document
        
    
    def _getPasswordFromNode(self, node):
        ''' Create password instance from given fpm node '''
        fields = ["title", "user", "url", "notes", "password"]
        params = {}
        for field in fields:
            params[field] = self._getTagData(node, field)
        
        # save default and launcher fields for fpm compatibility
        chnode = node.getElementsByTagName('default')
        if len(chnode)==1:
            params['default'] = 1
        params['launcher'] = self._getTagData(node, 'launcher')
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

    def encrypt(self, field, password=0):
        ''' Encrypt FPM encoded field '''
        hash=MD5.new()
        hash.update(self._salt + self._password)
        key = hash.digest()
        bf = Blowfish.new(key)
        noised = self._addNoise(field, password and FPM_PASSWORD_LEN)
        rotated = self._rotate(noised)
        encrypted = bf.encrypt(rotated)
        hexstr = self._bin_to_hex(encrypted)
        return hexstr

    def decrypt(self, field):
        ''' Decrypt FPM encoded field '''
        hash=MD5.new()
        hash.update(self._salt + self._password)
        key = hash.digest()
        bf = Blowfish.new(key)
        binstr = self._hex_to_bin(field)
        rotated = bf.decrypt(binstr)
        plaintext = self._unrotate(rotated)
        return plaintext

    def _bin_to_hex(self, strin):
        '''Used in encrypt'''
        strout = ""
        for i in range(len(strin)):
            data = strin[i]
            high = ord(data) / 16
            low = ord(data) % 16
            strout += chr(ord('a')+high) + chr(ord('a')+low)
        assert (2*len(strin) == len(strout))
        return strout

    def _hex_to_bin(self, strin):
        '''Used in decrypt'''
        strout = ""
        for i in range(len(strin) / 2):
            high = ord(strin[i * 2]) - ord('a')
            low = ord(strin[i * 2 + 1]) - ord('a')
            data = high * 16 + low
            assert data < 256
            strout = strout + chr(data)
        return strout

    def _addNoise(self, field, reslen = 0):         
        '''If we have a short string, I add noise after the first null prior to
        encrypting. This prevents empty blocks from looking identical to
        eachother in the encrypted file.'''
   
        block_size = Blowfish.block_size
        field += '\x00'
        reslen = reslen or (len(field) / block_size + 1) * block_size
        while len(field) < reslen:
            rchar = chr(randint(0, 255))
            field += rchar
        return field

    def _rotate(self, field):
        '''After we use _addNoise (above) we ensure blocks don't look identical
        unless all 8 chars in the block are part of the password.  This routine
        makes us use all three blocks equally rather than fill the first, then
        the second, etc.   This makes it so none of the blocks in the password
        will remain constant from save to save, even if the password is from
        7-20 characters long.  Note that passwords from 21-24 characters start
        to fill blocks, and so will be constant.  '''

        plaintext = ""
        tmp = {}
        block_size = Blowfish.block_size
        num_blocks = len(field)/block_size
        for b in range(num_blocks):
            for i in range(block_size):
                tmp[b*block_size+i] = field[i*num_blocks+b]

        for c in range(len(tmp)):
            plaintext = plaintext + tmp[c]
        return str(plaintext)

    def _unrotate(self, field):
        plaintext = ""
        tmp = {}
        block_size = Blowfish.block_size
        num_blocks = len(field)/block_size
        for b in range(num_blocks):
            for i in range(block_size):
                tmp[i*num_blocks+b] = field[b*block_size+i]

        for c in range(len(tmp)):
            if tmp[c] == chr(0):
                break
            plaintext = plaintext + tmp[c]
        return str(plaintext)
