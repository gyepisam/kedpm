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
# $Id: config.py,v 1.4 2003/10/12 20:39:49 kedder Exp $

"""Configuration for Ked Password Manager"""
from xml.dom import minidom
from UserDict import UserDict

# Configuration version
__version__ = "0.1"

class OptionError(ValueError):
    """Raised when option value validation fails"""
    pass

class Option:
    """Base class for all option types"""

    _value = None
    doc = ""
    def __init__(self, default=None, doc=""):
        self.set(default)
        self.doc = doc

    def __str__(self):
        return str(self._value)

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

class SelectOption (Option):
    """Option that can be set to value from known list of possible values"""

    __constraint = []
    
    def __init__(self, constraint, default = None, doc = ""):
        """constraint is a non-empty list of possible option values"""
        if type(constraint) != type([]) or not constraint:
            raise ValueError, "constraint must be a non-empty list"
        self.__constraint = constraint            
        Option.__init__(self, default, doc)
    
    def set(self, value):
        if value not in self.__constraint:
            raise OptionError, "Value must be one of %s" % self.__constraint
        self._value = value

class Options (UserDict):
    """List of self-validationg options"""

    def getOption(self, key):
        return UserDict.__getitem__(self, key)

    def __getitem__(self, key):
        return self.getOption(key).get()

    def __setitem__(self, key, value):
        self.getOption(key).set(value)

class Configuration:
    """Configuration file interface"""

    # Configuration file name
    filename = "doc/sample_config.xml"

    _options = {
        "save-mode": "ask"
    }

    options = Options({
        "save-mode": SelectOption(['ask', 'no', 'auto'], 'ask', """One of three values:
    "ask": Ask user whether save or not when database changes;
    "no": Do not save modified database automatically;
    "auto": Save database automatically after every change."""),
    })

    patterns = {}

    def __init__(self):
        #self.options = Options()
        pass
    
    def open(self, fname = ""):
        """Open and parse configuration xml file"""

        filename = fname or self.filename
        xml = minidom.parse(filename)
        doc = xml.documentElement

        sections = [
            ("options", "option", self.options),
            ("patterns", "pattern", self.patterns),
        ]
        
        # Read options
        tag = doc.getElementsByTagName('options')[0]
        items = tag.getElementsByTagName('option')
        for item in items:
            item_id = item.getAttribute("name")
            item_value = ""
            for child in item.childNodes:
                item_value += child.data
            try:
                #self.options[item_id].set(item_value)
                self.options[item_id] = item_value
            except KeyError:
                # Ignore unrecognized options
                pass
        # Read patterns
        tag = doc.getElementsByTagName('patterns')[0]
        items = tag.getElementsByTagName('pattern')
        for item in items:
            item_id = item.getAttribute("name")
            item_value = ""
            for child in item.childNodes:
                item_value += child.data
            self.patterns[item_id] = item_value

    def save(self):
        """Save configuration to xml file"""
        pass

