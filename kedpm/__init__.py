# KED Password Manager
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
# $Id: __init__.py,v 1.18 2010/02/09 23:57:45 eg1981 Exp $

''' KED Password Manager 

Simple to use, extensible and secure password manager
'''

import os

__version__ = '1.0'

data_files_dir = None

def setupPrefix():
    """Figure out base location where kedpm data files were installed by examining
    __file__ value. 
    
    On UNIX data files shoud be stored in <prefix>/share/kedpm directory."""

    global data_files_dir
    prefix_dir = __file__
    for i in range(5):
        prefix_dir, f = os.path.split(prefix_dir)
    data_files_dir = os.path.join(prefix_dir, 'share', 'kedpm')
    if not os.access(data_files_dir, os.F_OK):
        # We are in the distribution dir
        data_files_dir = "."

if data_files_dir is None:
    setupPrefix()

# Install gettext _() function
import gettext
gettext.install('kedpm', './po', unicode=0)
