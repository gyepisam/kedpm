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
# $Id: config.py,v 1.1 2003/10/03 22:08:56 kedder Exp $

"""Configuration for Ked Password Manager"""
from xml.dom import minidom

# Configuration version
__version__ = "0.1"

class Configuration:
    """Configuration implementation"""

    # Configuration file name
    filename = "doc/sample_config.xml"

    options = {
        "save-mode": "ask"
    }

    option_descriptions = {
        "save-mode": """One of three values:
    "ask": Ask user whether save or not when database changes;
    "no": Do not save modified database automatically;
    "auto": Save database automatically after every change."""
    }

    patterns = {}

    def __init__(self):
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
        for container_tag, item_tag, config_dict in sections:
            tag = doc.getElementsByTagName(container_tag)[0]
            items = tag.getElementsByTagName(item_tag)
            for item in items:
                item_id = item.getAttribute("name")
                item_value = ""
                for child in item.childNodes:
                    item_value += child.data
                config_dict[item_id] = item_value

    def save(self):
        """Save configuration to xml file"""
        pass

