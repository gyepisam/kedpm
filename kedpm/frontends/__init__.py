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
# $Id: __init__.py,v 1.3 2003/09/12 18:19:53 kedder Exp $

''' KED Password Manager - simple to use, extensible and secure password
manager.

This module contains frontends implementations.
Supported frontends::
    
    * cli - Command Line Interface frontend
    
    * gtk - GTK-2 frontend'''

def frontendFactory(frontend):
    if frontend == 'cli':
        from kedpm.frontends.cli import Application
        return Application()
    elif frontend == 'gtk':
        from kedpm.frontends.gtk.app import Application
        return Application()
    else:
        raise ValueError, '''Frontend "%s" is not supported.
Supported frontends are:
    cli: Command line interface;
    gtk: GTK2 graphical interface;''' % frontend


