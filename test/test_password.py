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
# $Id: test_password.py,v 1.3 2003/08/16 21:11:20 kedder Exp $

import unittest
from kedpm import password
from kedpm.password import Password

class PasswordTestCase(unittest.TestCase):
    def setUp(self):
        self.empty = Password()
        self.hostonly = Password(host='TheHost')
        self.hostname = Password(host='TheHost', name='TheName')
        self.full = Password(host='TheHost', name='TheName', password='Password')
        
    def test_getitem(self):
        self.assertEqual(self.empty['host'], '')
        self.assertEqual(self.hostonly['host'], 'TheHost')
        self.assertEqual(self.hostname['password'], '')
        self.assertEqual(self.full['name'], 'TheName')
        self.assertRaises(KeyError, self.full.__getitem__, 'NoSuchField')

    def test_setitem(self):
        self.empty['password'] = 'NewPassword'
        self.assertEqual(self.empty['password'], 'NewPassword')
        try:
            self.hostonly['NoSuchField'] = 'somevalue'
        except KeyError:
            pass
        else:
            assert 0, "__getattr__ doesn't raises KeyError on non-existant key"
        
    def test_getattr(self):        
        # __getattr__ method should work the same as getitem, so we will not
        # perform a full test
        self.assertEqual(self.empty.host, '')
        try:
            nsf = self.hostonly.NoSuchField
        except AttributeError:
            pass
        else:
            assert 0, "__getattr__ doesn't raises AttributeError on non-existant attribute"
    
    def test_setattr(self):
        # __setattr__ method should work the same as getitem, so we will not
        # perform a full test
        self.hostname.name = 'NewUsername'
        self.assertEqual(self.hostname.name, 'NewUsername')
        # __setattr__ must allow arbitary attributes to be set
        self.hostonly.NoSuchField = 'somevalue'
        self.assertEqual(self.hostonly.NoSuchField, 'somevalue')

    def test_asText(self):
        empty_asText = self.empty.asText()
        self.assertEqual(empty_asText, '')
        full_asText = self.full.asText()
        self.assertEqual(full_asText, '''Host: TheHost
Username: TheName
Password: Password
''')
        hostonly_asText = self.hostonly.asText()
        self.assertEqual(hostonly_asText, '''Host: TheHost
''')

    def test_getFieldsOfType(self):
        fields = self.full.getFieldsOfType()
        self.assertEqual(fields, ['host', 'name', 'password'])
        fields = self.full.getFieldsOfType([password.TYPE_STRING])
        self.assertEqual(fields, ['host', 'name'])
        fields = self.full.getFieldsOfType([password.TYPE_PASSWORD])
        self.assertEqual(fields, ['password'])
        fields = self.full.getFieldsOfType([password.TYPE_TEXT, password.TYPE_STRING, password.TYPE_PASSWORD])
        self.assertEqual(fields, ['host', 'name', 'password'])

    def test_getSearhableFields(self):
        fields = self.empty.getSearhableFields()
        self.assertEqual(fields, ['host', 'name'])        
    
def suite():
    return unittest.makeSuite(PasswordTestCase, 'test')

if __name__ == "__main__":
    unittest.main()
