#!/usr/bin/env python
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
# $Id: setup.py,v 1.3 2003/08/26 21:33:57 kedder Exp $

from distutils.core import setup
from kedpm import __version__
import os, sys

def main():
    
    long_description = """Ked Password Manager helps to manage large amounts of
passwords and related information and simplifies tasks of searching and
entering password data.

Ked-PM written as extensible framework, which allows to plug in custom password
database back-ends and custom user interface front-ends. Currently only Figaro
PM back-end and command line interface front-end supported."""
    
    setup(
        name="kedpm",
        version=__version__,
        description="Ked Password Manager",
        long_description = long_description,
        author="Andrey Lebedev",
        author_email="andrey@users.sourceforge.net",
        url="http://kedpm.sourceforge.net/",
        packages=['kedpm', 'kedpm.plugins', 'kedpm.frontends', 'kedpm.frontends.gtk'],
        scripts=['kedpm-cli'],
        data_files=[(os.path.join('share', 'kedpm'), ['AUTHORS', 'COPYING', 'INSTALL'])],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Security',
            'Topic :: Utilities'
        ]
    )

if __name__ == '__main__':
    main()
