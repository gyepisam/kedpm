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
# $Id: test_config.py,v 1.7 2004/02/24 22:58:46 kedder Exp $

import unittest

from kedpm.config import Configuration, Options, Option, SelectOption

class ConfigTestCase(unittest.TestCase):
    def setUp(self):
        self.conf = Configuration()
        self.conf.filename = "test/sample_config.xml"
        self.conf.open()
        
    def test_readConfig(self):
        self.assertEqual(self.conf.options["save-mode"], "ask")
        self.assertEqual(len(self.conf.patterns), 2)
        self.assertEqual(self.conf.patterns[0],
                "Username/Password: {user}/{password}")

class OptionsTestCase(unittest.TestCase):
    def test_option(self):
        opt = Option('value', 'doc')
        self.assertEqual(opt.get(), 'value')
        self.assertEqual(opt.doc, 'doc')
        
    def test_options(self):
        options = Options({
            "save-mode": Option('ask', "Doc string"),
        })
        #import pdb; pdb.set_trace() 
        self.assertEqual(options['save-mode'], 'ask')
        self.assertEqual(options.getOption('save-mode').doc, 'Doc string')

    def test_selectOption(self):
        self.assertRaises(ValueError, SelectOption, [])
        opt = SelectOption(["ask", "no", "auto"], 'ask', "Doc string")
        self.assertRaises(ValueError, opt.set, "bad")
        opt.set("auto")
        self.assertEqual(opt.get(), "auto")
        

def suite():
    l = [
        unittest.makeSuite(ConfigTestCase, 'test'),
        unittest.makeSuite(OptionsTestCase, 'test'),
    ]
    return unittest.TestSuite(l)

if __name__ == "__main__":
    unittest.main()
