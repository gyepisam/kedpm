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
# $Id: test_password_tree.py,v 1.1 2003/08/05 18:32:18 kedder Exp $

import unittest
from kedpm.password_tree import PasswordTree
from kedpm.password import Password

class PasswordTreeTestCase(unittest.TestCase):
    def setUp(self):
        self.ptree = PasswordTree()
        self.pass1 = Password("host1", "name1", "password1")
        self.pass2 = Password("host2", "name2", "password2")
        self.ptree.addNode(self.pass1)
        self.ptree.addNode(self.pass2)
        self.subdir = self.ptree.addBranch("subdir")
        self.pass3 = Password("host3", "name3", "password3")
        self.subdir.addNode(self.pass3)
        
    def test_create(self):
        assert self.ptree

    def test_nodes(self):
        nodes = self.ptree.getNodes()
        self.assertEqual(len(nodes), 2)
        self.assertEqual(nodes, [self.pass1, self.pass2])

    def test_branches(self):
        branches = self.ptree.getBranches()
        self.assertEqual(len(branches), 1)
        self.assertRaises(AttributeError, self.ptree.addBranch, 'subdir')
        subdir = self.ptree['subdir']
        self.assertEqual(subdir.getNodes(), [self.pass3])

    def test_locate(self):
        found = self.ptree.locate('name')
        self.assertEqual(found, [self.pass1, self.pass2])
        found = self.ptree.locate('st1')
        self.assertEqual(found, [self.pass1])
        found = self.ptree.locate('sword')
        self.assertEqual(found, [])

    def test_normalizePath(self):
        testpath1 = ['dir', 'subdir', 'subsubdir']
        npath = self.ptree.normalizePath(testpath1)
        self.assertEqual(npath, testpath1)
        npath = self.ptree.normalizePath(['dir', 'subdir', 'subsubdir', '..'])
        self.assertEqual(npath, ['dir', 'subdir'])
        npath = self.ptree.normalizePath(['..', 'dir', 'subdir', 'subsubdir'])
        self.assertEqual(npath, testpath1)
        npath = self.ptree.normalizePath(['dir', '.', 'subdir', 'subsubdir', '.'])
        self.assertEqual(npath, testpath1)

    def test_getTreeFromPath(self):
        root = self.ptree.getTreeFromPath(['.'])
        self.assertEqual(root, self.ptree)
        root = self.ptree.getTreeFromPath(['..'])
        self.assertEqual(root, self.ptree)
        root = self.ptree.getTreeFromPath(['subdir'])
        self.assertEqual(root, self.subdir)
                            
def suite():
    return unittest.makeSuite(PasswordTreeTestCase, 'test')

if __name__ == "__main__":
    unittest.main()
