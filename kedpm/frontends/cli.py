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
# $Id: cli.py,v 1.1 2003/08/05 18:32:18 kedder Exp $

from kedpm.plugins.pdb_figaro import PDBFigaro
from kedpm.exceptions import WrongPassword
from getpass import getpass
from cmd import Cmd
import sys

class Frontend (Cmd):
    PS1 = "kedpm:%s> " # prompt template
    pwd = []
    intro = """KED Password Manager is ready for operation.
try 'help' for brief description of available commands
"""
    
    def openDatabase(self):
        ''' Open database amd prompt for password if nesessary '''
        self.pdb = PDBFigaro()
        password = ""
        while 1:
            try:
                self.pdb.open(password)
                break
            except WrongPassword:
                if password:
                    print "Error! Wrong password."
                else: 
                    print "Provide password to access the database"
                try:
                    password = getpass("Password: ")
                except EOFError:
                    print
                    print "Good bye."
                    sys.exit(1)
    
    def updatePrompt(self):
        self.prompt = self.PS1 % ('/'+'/'.join(self.pwd))

    def getPwd(self):
        return self.pdb.getTree().getTreeFromPath(self.pwd)

    def listPasswords(self, passwords, show_numbers=0):
        '''display given passwords in nicely formed table'''
        # we assume that all passwords in list have the same fields
        # the same as in first one
        if not passwords:
            return
        prot = passwords[0]
        lengths = show_numbers and {'nr': 3} or {}
        headers = show_numbers and ['Nr'] or []
        fstr = show_numbers and "%%%ds " or ""
        listable = prot.listable
        if show_numbers:
            listable = ['nr'] + listable
        # determine maximum space needed by each column
        for fld in prot.listable:
            lengths[fld] = len(prot.fields[fld])
            fstr = fstr + "%%%ds "
            headers.append(prot.fields[fld])
        
        ptuples = []
        num = 1
        for pwd in passwords:
            ptup = []
            if show_numbers:
                ptup.append("%d)" %num)
            for fld in pwd.listable:
                ptup.append(getattr(pwd, fld))
                newlen = len(getattr(pwd, fld))
                if  newlen > lengths[fld]:
                    lengths[fld] = newlen
            ptuples.append(tuple(ptup))
            num = num + 1
        # form format string
        fstr = fstr % tuple([lengths[x]+1 for x in listable])
        print fstr % tuple(headers)
        print fstr % tuple(["="*lengths[x]for x in listable])
        for ptup in ptuples:
            print fstr % ptup

    def emptyline(self):
        pass
    
    def do_exit(self, arg):
        '''Quit KED Password Manager'''
        print "Exiting."
        sys.exit()

    def do_EOF(self, arg):
        '''The same as 'exit' command'''
        print
        self.do_exit(arg)

    def do_help(self, arg):
        '''Print help message'''
        Cmd.do_help(self, arg)

    def do_ls(self, arg):
        '''List available catalogs and passwords'''
        root_tree = self.getPwd()
        if not arg:
            # list current dir
            tree = root_tree
        else:
            # list given dir
            dir = arg
            tree = root_tree[dir]
        print "=== Directories ==="
        for (bname) in tree.getBranches():
            print bname+"/"
        print "==== Passwords ===="
        self.listPasswords(tree.getNodes())
        #for password in tree.getNodes():
        #    print password.name
    
    def do_cd(self, arg):
        ''' change directory (catalog)'''
        root =  self.pdb.getTree()
        cdpath = root.normalizePath(arg.split('/'))
        try:
            newpath = root.getTreeFromPath(cdpath)
        except KeyError:
            print "cd: %s: No such catalog" % arg
        else:
            self.pwd = cdpath
            self.updatePrompt()

    def do_pwd(self, arg):
        '''print name of current/working directory'''
        print '/'+'/'.join(self.pwd)
    
    def do_show(self, arg):
        '''display password information'''
        pwd = self.getPwd()
        passwords = pwd.locate(arg)
        if not passwords:
            print "No passwords matching \"%s\" found" % arg
            return
        self.listPasswords(passwords, 1)
        print "Enter number to show. 0 returns to command prompt"
        showstr = raw_input('show: ')
        try:
            shownr = int(showstr)
            if not shownr:
                return
            selected_password = passwords[shownr-1]
        except (ValueError, IndexError):
            return
        print selected_password.asText()
    
    def run(self):
        self.openDatabase()
        self.updatePrompt()
        self.cmdloop()
