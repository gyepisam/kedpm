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
# $Id: setup.py,v 1.8 2004/02/29 11:45:48 kedder Exp $

from distutils.core import setup
from kedpm import __version__
import os, sys
from glob import glob

# patch distutils if it can't cope with the "classifiers" keyword
# that's support for python < 2.3
from distutils.dist import DistributionMetadata
if not hasattr(DistributionMetadata, 'classifiers'):
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None


def main():
    
    long_description = """Ked Password Manager helps to manage large amounts of
passwords and related information and simplifies tasks of searching and
entering password data.

Ked-PM written as extensible framework, which allows to plug in custom password
database back-ends and custom user interface front-ends. Currently only Figaro
PM back-end. To control KedPM user can choose between  CLI and GTK2 based GUI
front-ends."""
    
    setup(
        name="kedpm",
        version=__version__,
        description="Ked Password Manager",
        long_description = long_description,
        author="Andrey Lebedev",
        author_email="andrey@users.sourceforge.net",
        license="GPL",
        platforms="POSIX",
        url="http://kedpm.sourceforge.net/",
        packages=['kedpm', 'kedpm.plugins', 'kedpm.frontends', 'kedpm.frontends.gtk'],
        scripts=['scripts/kedpm'],
        data_files=[(os.path.join('share', 'kedpm'), ['AUTHORS', 'COPYING', 'INSTALL']),
            (os.path.join('share', 'kedpm', 'glade'),
                [os.path.join('glade', 'kedpm.glade')] +
                glob(os.path.join('glade', '*.png'))
                )],
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: X11 Applications :: GTK',
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
