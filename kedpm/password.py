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
# $Id: password.py,v 1.6 2003/09/21 18:18:08 kedder Exp $

""" Password item """

# type constants
TYPE_STRING = 'string'
TYPE_TEXT = 'text'
TYPE_PASSWORD = 'password'

class Password:
    """ Basic class for password structure """
    
    fields_type_info = [
        ('host',     {'title': 'Host', 'type': TYPE_STRING}),
        ('name',     {'title': 'Username', 'type': TYPE_STRING}),
        ('password', {'title': 'Password', 'type': TYPE_PASSWORD}),
    ]

    _fields = {}

    def __init__(self, **kw):
        self._fields = {}
        for key, fieldinfo in self.fields_type_info:
            finfo  = fieldinfo.copy()
            finfo['value'] = kw.get(key, "")
            self._fields[key] = finfo

    def __getitem__(self, key):
        return self._fields[key]['value']

    def __setitem__(self, key, value):
        if self._fields.has_key(key):
            self._fields[key]['value'] = value
        else:
            raise KeyError, "No such field in this password"

    def update(self, info):
        for k in self._fields.keys():
            if info.has_key(k):
                self[k] = info[k]

    def __getattr__(self, name):
        try:
            attr = self[name]
        except KeyError, message:
            raise AttributeError, message
        return attr

    def __setattr__(self, name, value):
        try:
            self[name] = value
        except KeyError, message:
            self.__dict__[name] = value
    
    def getField(self, name):
        '''Returns field descriptor'''
        for key, fieldinfo in self.fields_type_info:
            if key==name:
                return fieldinfo      
        else: 
            raise KeyError, 'No such field defined'
    
    def getFieldTitle(self, name):
        '''Returns title of field "name"'''
        title = ""
        try:
            title = self.getField(name)['title']
        except KeyError:
            pass
        return title

    def getFieldsOfType(self, types = []):
        '''Returns all fields of type listed in types list. If types is empty
        list, return all fields.'''
        res = []
        for key, fieldinfo in self.fields_type_info:
            if fieldinfo['type'] in types or types == []:
                res.append(key)
        return res

    def getSearhableFields(self):
        '''Returns list of fields that can be searched on. Practically this
        means all fields except TYPE_PASSWORD'''
        return self.getFieldsOfType([TYPE_STRING, TYPE_TEXT])

    def asText(self):
        'Returns plain text representation of the password'
        astext = ""
        for key, fieldinfo in self.fields_type_info:
            if self[key] == '':
                continue
            astext += "%s: %s\n" % (fieldinfo['title'], self[key])
        return astext
            
