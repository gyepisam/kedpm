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
# $Id: test_figaro.py,v 1.2 2003/08/06 20:37:28 kedder Exp $

import unittest
from kedpm.plugins.pdb_figaro import PDBFigaro

class PDBFigaroTestCase(unittest.TestCase):
    password = 'password'
    def setUp(self):
        self.pdb = PDBFigaro()
        self.pdb.open(self.password, fname='test/fpm.sample')

    def test_create(self):
        assert isinstance(self.pdb, PDBFigaro)

    def test_tree(self):
        ptree = self.pdb.getTree()
        branches = ptree.getBranches()
        self.assertEqual(branches.keys(), ['Test', 'Kedder'])
        tree_test = ptree['Test']
        assert tree_test
        self.assertEqual(len(tree_test.getNodes()), 2)
        tree_kedder = ptree['Kedder']
        assert tree_kedder
        self.assertEqual(len(tree_kedder.getNodes()), 1)

    def test_decription(self):
        tree_test = self.pdb.getTree()['Test']
        pwds = tree_test.locate('url')
        self.assertEqual(len(pwds), 2)
        pwd_test2 = tree_test.locate('test2')
        self.assertEqual(pwd_test2[0].password, 'test2 password')
        

def suite():
    return unittest.makeSuite(PDBFigaroTestCase, 'test')

if __name__ == "__main__":
    unittest.main()

