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
# $Id: test_password_tree.py,v 1.4 2003/08/16 21:11:20 kedder Exp $

import unittest
from kedpm.password_tree import PasswordTree
from kedpm.password import Password

class PasswordTreeTestCase(unittest.TestCase):
    def setUp(self):
        self.ptree = PasswordTree()
        self.pass1 = Password(host = "host1", name = "name1", password = "password1")
        self.pass2 = Password(host = "host2", name = "name2", password = "password2")
        self.ptree.addNode(self.pass1)
        self.ptree.addNode(self.pass2)
        self.subdir = self.ptree.addBranch("subdir")
        self.pass3 = Password(host = "host3", name = "name3", password = "password3")
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

class PasswordTreeIteratorTestCase(unittest.TestCase):
    def setUp(self):
        # We will form such tree here:
        # root
        #  +-br1
        #    +-br1.1
        #      +-pw0
        #      +-pw1
        #    +-pw2
        #    +-pw3
        #  +-br2
        #    +-br2.1
        #      +-pw4
        #    +-br2.2
        #      +-pw5
        #      +-pw6
        #    +-pw7
        #  +-pw8
        #  +-pw9
        #
        self.pwds = []
        for i in range(10):
            pwd = Password(host = "host%d" % i, name = "name%d" % i , password = "password%d" % i)
            self.pwds.append(pwd)

        ptree = PasswordTree()
        br1 = ptree.addBranch('br1')
        br11 = br1.addBranch('br2')
        br11.addNode(self.pwds[0])
        br11.addNode(self.pwds[1])
        br1.addNode(self.pwds[2])
        br1.addNode(self.pwds[3])
        
        br2 = ptree.addBranch('br2')
        br2.addNode(self.pwds[7])
        br21 = br2.addBranch('br21')
        br22 = br2.addBranch('br22')
        br21.addNode(self.pwds[4])
        br22.addNode(self.pwds[5])
        br22.addNode(self.pwds[6])
        ptree.addNode(self.pwds[8])
        ptree.addNode(self.pwds[9])       
        
        self.ptree = ptree

    def test_getCurrentCategory(self):
        iter = self.ptree.getIterator()
        iter.next() # pw0
        self.assertEqual(iter.getCurrentCategory(), 'br1')
        iter.next() # pw1
        iter.next() # pw2
        self.assertEqual(iter.getCurrentCategory(), 'br1')
        iter.next() # pw3
        iter.next() # pw4
        iter.next() # pw5
        iter.next() # pw6
        self.assertEqual(iter.getCurrentCategory(), 'br2')
        iter.next() # pw7
        iter.next() # pw8
        self.assertEqual(iter.getCurrentCategory(), '')

    def test_order(self):
        iter = self.ptree.getIterator()
        for i in range(10):
            pwd = iter.next()
            self.assertEqual(pwd, self.pwds[i])
        pwd = iter.next()
        self.assertEqual(pwd, None)
        pwd = iter.next()
        self.assertEqual(pwd, None)
         
def suite():
    l = [
        unittest.makeSuite(PasswordTreeTestCase, 'test'),
        unittest.makeSuite(PasswordTreeIteratorTestCase, 'test')
    ]
    return unittest.TestSuite(l)

if __name__ == "__main__":
    unittest.main()
