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
# $Id: config.py,v 1.8 2004/01/18 16:29:20 kedder Exp $

"""Configuration for Ked Password Manager"""
import os
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

class FileOption (Option):
    """Option containing filename"""
    pass

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

    def getConstraint(self):
        """Return available valid values"""
        return self.__constraint

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
    #filename = "doc/sample_config.xml"
    filename = os.getenv('HOME') + '/.kedpm/config.xml'

    options = Options({
        "save-mode": SelectOption(['ask', 'no', 'auto'], 'ask', """One of three values:
    "ask": Ask user whether save or not when database changes;
    "no": Do not save modified database automatically;
    "auto": Save database automatically after every change."""),

        "fpm-database": FileOption('~/.fpm/fpm', """Filename where all passwords are stored.
Changes will take effect after kedpm restart."""),
    })

    default_patterns = [
        "User{~(name)?}/Pass{~(word)?}{ }:{ }{user}/{password}",
        "User{~(name)?}{ }:{ }{user}",
        "Pass{~(word)?}{ }:{ }{password}",
        "Host{~(name)?}{ }:{ }{url}",
        "Server{ }:{ }{url}"
    ]
    patterns = []

    def __init__(self):
        #self.options = Options()
        pass
    
    def open(self):
        """Open and parse configuration xml file"""
        # Check if config file is readable
        if not os.access(self.filename, os.R_OK):
            # Config isn't readable. Try to create default one
            self.create()
            
        xml = minidom.parse(self.filename)
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
            self.patterns.append(item_value)
        if not self.patterns:
            self.patterns = self.default_patterns

    def save(self):
        """Save configuration to xml file"""
        document = self.buildDOM()
        configfile = open(self.filename, "w")
        configfile.write(document.toxml())
        configfile.close()

    def create(self):
        """Initialise new configuration
        
        Create dot-directory in homedir and save initial configuration."""

        dirname, fname = os.path.split(self.filename)
        if not os.access(dirname, os.F_OK):
            print "Creating directory %s" % dirname
            os.mkdir(dirname, 0700)
        self.save()

    def buildDOM(self):
        """Build DOM object for current configuration"""
        domimpl = minidom.getDOMImplementation()
        document= domimpl.createDocument("http://kedpm.sourceforge.net/xml/fpm", "config", None)
        root = document.documentElement
        root.setAttribute('verion', __version__)
        
        # Add options
        options = document.createElement('options')
        root.appendChild(options)
        for optname, optvalue in self.options.items():
            opt_node = document.createElement('option')
            opt_node.setAttribute('name', optname)
            opt_node.appendChild(document.createTextNode(optvalue.get()))
            options.appendChild(opt_node)
            
        root.appendChild(document.createTextNode('\n'))
        # Add patterns
        patterns = document.createElement('patterns')
        root.appendChild(patterns)
        for pattern in self.patterns:
            pat_node = document.createElement('pattern')
            pat_node.appendChild(document.createTextNode(pattern))
            patterns.appendChild(pat_node)
            
        return document
        
