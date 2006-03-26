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
# $Id: test_config.py,v 1.8 2006/03/26 10:04:19 kedder Exp $

import os
import unittest

from kedpm.config import Configuration, Options, Option, SelectOption, BooleanOption

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

    def test_saveConfig(self):
        self.conf.options['verbose'] = True
        self.conf.options['confirm-deletes'] = 'yes'
        self.conf.filename = "test/saved_config.xml"
        self.conf.save()
        self.conf.open()
        self.assertEqual(self.conf.options['verbose'], True)
        self.assertEqual(self.conf.options['confirm-deletes'], True)
        os.unlink('test/saved_config.xml')

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
