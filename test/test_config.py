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
# $Id: test_config.py,v 1.2 2003/10/09 21:12:06 kedder Exp $

import unittest

from kedpm.config import Configuration

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.conf = Configuration()
        self.conf.open(fname="test/sample_config.xml")
        
    def test_readConfig(self):
        self.assertEqual(self.conf.options["save-mode"].get(), "ask")
        self.assertEqual(len(self.conf.patterns), 2)
        self.assertEqual(self.conf.patterns["sample1"], 
                "Username/Password: {user}/{password}")


def suite():
    return unittest.makeSuite(ConfigTestCase, 'test')

if __name__ == "__main__":
    unittest.main()
