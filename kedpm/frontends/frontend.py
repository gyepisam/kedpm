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
# $Id: frontend.py,v 1.4 2004/01/04 17:07:16 kedder Exp $

'''Ked Password Manager frontend abstraction.'''

from shutil import copyfile
import sys

from kedpm.config import Configuration

class Frontend:
    conf = None  # Configuration object
    def mainLoop(self):
        '''Main loop of frontend application here.'''
        raise NotImplementedError
        
    def showMessage(self, message):
        '''Display an information message'''
        raise NotImplementedError

    def openDatabase(self):
        """Opend database. (set self.pdb variable)
        
        Prompt user for password if necessary. If no database exists yet,
        create empty one, asking user for necessary information.
        """ 
        raise NotImplementedError
    
    def run(self):
        '''Run frontnend program
        
        Do common initialisation stuff common to all frontends,'''

        # Open configuration
        self.conf = Configuration()
        self.conf.open()
        # Open database
        try:
            self.openDatabase()
        except (EOFError, KeyboardInterrupt):
            print
            print "Good bye."
            sys.exit(1)
        if not self.pdb.native:
            # Do backup
            backupfile = self.pdb.default_db_filename+'.kedpm.bak'
            self.showMessage("""WARNING! KedPM has detected original FPM password database.
Backing it up to %s
""" % backupfile)
            copyfile(self.pdb.default_db_filename, backupfile)
        
        self.mainLoop()
