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
# $Id: cli.py,v 1.24 2003/10/18 20:26:36 kedder Exp $

"Command line interface for Ked Password Manager"

from kedpm import __version__
from kedpm.plugins.pdb_figaro import PDBFigaro, FigaroPassword, FigaroPasswordTooLongError
from kedpm.passdb import DatabaseNotExist
from kedpm.exceptions import WrongPassword, RenameError
from kedpm.frontends.frontend import Frontend
from kedpm.config import OptionError
from kedpm import password
from kedpm import parser
from getpass import getpass
from cmd import Cmd
import os, sys, tempfile

class Application (Cmd, Frontend):
    PS1 = "kedpm:%s> " # prompt template
    pwd = []
    intro = """Ked Password Manager is ready for operation.
try 'help' for brief description of available commands
"""

    modified = 0
    
    def openDatabase(self):
        ''' Open database amd prompt for password if nesessary '''
        self.pdb = PDBFigaro()
        password = ""
        print "Ked Password Manager (version %s)" % __version__
        while 1:
            try:
                self.pdb.open(password)
                break
            except WrongPassword:
                if password:
                    print "Error! Wrong password."
                else: 
                    print "Provide password to access the database (Ctrl-C to exit)"
                password = getpass("Password: ")
            except DatabaseNotExist:
                password = self.createNewDatabase()
        print "Password accepted."
        print

    def createNewDatabase(self):
        'Create new password database and return password for created database'
        print "Creating new password database."
        pass1 = pass2 = ""
        while pass1 != pass2 or pass1 == "":
            pass1 = getpass("Provide password: ")
            pass2 = getpass("Repeat password: ")
            if pass1 == '':
                print "Empty passwords are really insecure. You shoud create one."
            if pass1!=pass2:
                print "Passwords don't match! Please repeat."

        self.pdb.create(pass1)
        return pass1

    def updatePrompt(self):
        self.prompt = self.PS1 % ('/'+'/'.join(self.pwd))

    def getPwd(self):
        'Return current password tree instance'
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
        listable = prot.getFieldsOfType([password.TYPE_STRING])
        # determine maximum space needed by each column
        for fld in listable:
            ftitle = prot.getFieldTitle(fld)
            lengths[fld] = len(ftitle)
            fstr = fstr + "%%%ds "
            headers.append(ftitle)
        
        ptuples = []
        num = 1
        for pwd in passwords:
            ptup = []
            if show_numbers:
                ptup.append("%d)" %num)
            for fld in listable:
                ptup.append(getattr(pwd, fld))
                newlen = len(getattr(pwd, fld))
                if  newlen > lengths[fld]:
                    lengths[fld] = newlen
            ptuples.append(tuple(ptup))
            num = num + 1
        # form format string
        if show_numbers:
            listable = ['nr'] + listable
        fstr = fstr % tuple([lengths[x]+1 for x in listable])
        print fstr % tuple(headers)
        print fstr % tuple(["="*lengths[x]for x in listable])
        for ptup in ptuples:
            print fstr % ptup

    def pickPassword(self, regexp):        
        '''Prompt user to pick one password from located list. If list contains
        only one password, return it without prompting. If no passwords were
        located, or user desides to cancel operation, return None'''

        pwd = self.getPwd()
        passwords = pwd.locate(regexp)
        if not passwords:
            print "No passwords matching \"%s\" were found" % regexp
            return None
        if len(passwords) > 1:
            self.listPasswords(passwords, 1)
            print "Enter number. Enter 0 to cancel."
            showstr = raw_input('show: ')
            try:
                shownr = int(showstr)
                if not shownr:
                    return None
                selected_password = passwords[shownr-1]
            except (ValueError, IndexError):
                return None
        else:
            selected_password = passwords[0]
        return selected_password

    def inputString(self, prompt):
        '''Input string from user'''
        input = raw_input(prompt)
        return input

    def inputText(self, prompt):
        '''Input long text from user'''
        return self.inputString(prompt)

    def inputPassword(self, prompt):
        '''Input long text from user'''
        pwd = None
        while pwd is None:
            pass1 = getpass(prompt)
            if pass1=='':
                return ''
            pass2 = getpass('Repeat: ')
            if pass1==pass2:
                pwd = pass1
            else:                
                print "Passwords don't match. Try again."
        return pwd
        

    def editPassword(self, pwd):
        '''Prompt user for each field of the password. Respect fields' type.'''

        input = {}
    
        for field, fieldinfo in pwd.fields_type_info:
            field_type = fieldinfo['type']
            
            new_value = ""
            if field_type == password.TYPE_STRING:
                new_value = self.inputString("Enter %s (\"%s\"): " % (pwd.getFieldTitle(field), pwd[field]))
            elif field_type == password.TYPE_TEXT:
                new_value = self.inputText("Enter %s (\"%s\"): " % (pwd.getFieldTitle(field), pwd[field]))
            elif field_type == password.TYPE_PASSWORD:
                new_value = self.inputPassword("Enter %s: " % pwd.getFieldTitle(field))
            else:
                print """Error. Type %s is unsupported yet. This field will retain an old value.""" % field_type

            if new_value!="":
                input[field] = new_value

        try:
            pwd.update(input)
        except FigaroPasswordTooLongError:
            print "WARNING! Your password is too long for Figaro Password Manager."
            print "Figaro Password Manager can handle only passwords shorter than 24 characters."
            print """However, KedPM can store this password for you, but it
will break fpm compatibility. fpm will not be able to handle such
long password correctly."""
            answer = raw_input("Do you still want to save your password? [Y/n]: ")
            if answer.lower().startswith('n'):
                raise KeyboardInterrupt
            pwd.store_long_password = 1
            pwd.update(input)

        #return pwd

    def tryToSave(self):
        
        self.modified = 1
        savemode = self.conf.options["save-mode"]
        if savemode == 'no':
            return
        answer = 'y'
        if self.conf.options["save-mode"] == "ask":
            answer = raw_input("Database was modified. Do you want to save it now? [Y/n]: ")            
        if answer=='' or answer.lower().startswith('y'):
            self.do_save('')
    
    def complete_dirs(self, text, line, begidx, endidx):
        dirs=self.pdb.getTree().getBranches()
        compl = []
        for dir in dirs:
            if dir.startswith(text):
                compl.append(dir)
        return compl
    
    def getEditorInput(self):
        """Fire up default editor and read user input from temporary file"""
        default_editor = "vi"
        if os.environ.has_key('VISUAL'):
            editor = os.environ['VISUAL']
        elif os.environ.has_key('EDITOR'):
            editor = os.environ['EDITOR']
        else: 
            editor = default_editor
        print "running %s" % editor
        # create temporary file
        handle, tmpfname = tempfile.mkstemp(prefix="kedpm_")
        os.system(editor + " " + tmpfname)
        tmpfile = open(tmpfname, 'r')
        text = tmpfile.read()
        tmpfile.close()
        os.remove(tmpfname)
        return text

    def parseMessage(self, text, pwd):
        """Extract valuable password information from text and return filled password"""
        choosendict = {}
        for pattern in parser.patterns:
            regexp = parser.regularize(pattern)
            passdict = parser.parse(regexp, text)
            if len(passdict) > len(choosendict):
                choosendict = passdict

        print "Choosen dict: %s" % str(choosendict)    
        pwd.update(choosendict)
    
    ##########################################
    # Command implementations below.         #
        
    def emptyline(self):
        pass
    
    def do_exit(self, arg):
        '''Quit KED Password Manager'''
        if self.modified:
            self.tryToSave()
        print "Exiting."
        sys.exit(0)

    def do_EOF(self, arg):
        '''The same as 'exit' command'''
        print
        self.do_exit(arg)

    def do_help(self, arg):
        '''Print help message'''
        Cmd.do_help(self, arg)

    def do_ls(self, arg):
        '''List available catalogs and passwords
Syntax:
    ls [<category>]
'''
        root_tree = self.getPwd()
        if not arg:
            # list current dir
            tree = root_tree
        else:
            # list given dir
            try:
                tree = root_tree[arg]
            except KeyError:
                print "ls: %s:  No such catalog" % arg
                return
        print "=== Directories ==="
        for bname in tree.getBranches().keys():
            print bname+"/"
        print "==== Passwords ===="
        self.listPasswords(tree.getNodes())

    def complete_ls(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)
    
    def do_cd(self, arg):
        '''change directory (catalog)
 
Syntax:
    cd <category>
'''
        root =  self.pdb.getTree()
        cdpath = root.normalizePath(arg.split('/'))
        try:
            newpath = root.getTreeFromPath(cdpath)
        except KeyError:
            print "cd: %s: No such catalog" % arg
        else:
            self.pwd = cdpath
            self.updatePrompt()

    def complete_cd(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)
    
    def do_pwd(self, arg):
        '''print name of current/working directory'''
        print '/'+'/'.join(self.pwd)
    
    def do_show(self, arg):
        '''display password information.
        
Syntax:
    show <regexp>

This will display contents of a password item in current category. If
several items matched by <regexp>, list of them will be printed and you will be
prompted to enter a number, pointing to password you want to look at.
After receiving that number, KedPM will show you the password.
'''
        
        selected_password = self.pickPassword(arg)
        if selected_password:
            print "---------------------------------------"
            print selected_password.asText()
            print "---------------------------------------"
        else:
            print "No password selected"

    def do_edit(self, arg):
        '''edit password information.
        
Syntax:
    edit <regexp>
            
This will prompt you for editing of a password item in current category. If
several items matched by <regexp>, list of them will be printed and you will be
prompted to enter a number, pointing to password you want to edit.  After
receiving that number, you will be able to edit picked password.  

'''

        selected_password = self.pickPassword(arg)
        if selected_password:
            try:
                self.editPassword(selected_password)
                #self.modified = 1
                self.tryToSave()
            except (KeyboardInterrupt, EOFError):
                print "Cancelled"
        else:
            print "No password selected"

    def do_new(self, arg):
        '''Add new password to current category. You will be prompted to enter
fields.
    
Syntax:
    new [-p]

    -p - Get properties by parsing provided text. Will open default text editor
         for you to paste text in.
'''
        new_pass = FigaroPassword() # FIXME: Password type shouldn't be hardcoded.
        argv = arg.split()

        if "-p" in argv:
            text = self.getEditorInput()
            self.parseMessage(text, new_pass)
        
        try:
            self.editPassword(new_pass)
        except (KeyboardInterrupt, EOFError):
            print "Cancelled"
        else:
            tree = self.getPwd()
            tree.addNode(new_pass)
            #self.modified = 1
            self.tryToSave()

    def do_save(self, arg):
        '''Save current password tree'''
        sys.stdout.write("Saving...")
        sys.stdout.flush()
        self.pdb.save()
        print "OK"
        self.modified = 0

    def do_mkdir(self, arg):
        '''create new category (directory)
        
Syntax:
    mkdir <category>
            
Creates new password category in current one.
'''
        if not arg:
            print "mkdir: too few arguments"
            print "try 'help mkdir' for more information"
            return

        pwd = self.getPwd()
        pwd.addBranch(arg.strip())

    def do_rename(self, arg):
        '''rename category
        
Syntax:
    rename <category> <new_name>
'''
        args = arg.split()
        if len(args) != 2:
            print '''Syntax:
    rename <category> <new_name>
'''
            return
        oldname = args[0]
        newname = args[1]
        try:
            self.pdb.getTree().renameBranch(self.pwd+[oldname], newname)
        except RenameError:
            print "rename: category %s already exists" % newname
            return
        except KeyError:
            print "rename: %s: no such category" % oldname
            return
        self.tryToSave()

    def complete_rename(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)

    def do_help(self, arg):
        """Print help topic"""
        argv = arg.split()
        if argv and argv[0] in ['set']:
            # Provide extended help
            help_def = getattr(self, "help_"+argv[0])
            if help_def:
                help_def(' '.join(argv[1:]))
            else: 
                Cmd.do_help(self, arg)
        else:
            Cmd.do_help(self, arg)

    def do_set(self, arg):
        """Set KedPM options

Syntax:
    set                     -- show all options
    set <option>            -- show value of option
    set <option> = <value>  -- set value to option

for boolean values 1, 'on' or 'true' are considered as True; 0, 'off' or 'false' are
considered as False.

enter help set <option> for more info on particular option."""
        
        opts = self.conf.options
        if not arg:
            # show all options
            for opt, value in opts.items():
                print "%s = %s" % (opt, value)
            return
        tokens = arg.split('=')
        opt_name = tokens[0]
        try:
            opt_value = opts[opt_name]
        except KeyError:
            print "set: no such option: %s" % arg
            return
        if len(tokens) == 1:
            # show value of option
            print "%s = %s" % (opt_name, opt_value)
        else:
            # set the value
            try:
                opts[opt_name] = ' '.join(tokens[1:])
            except OptionError, e:
                print "set: %s" % e
        # save confuguration file
        self.conf.save()
        
    def complete_set(self, text, line, begidx, endidx):
        compl = []
        #print self.conf.options
        for opt in self.conf.options.keys():
            if opt.startswith(text):
                compl.append(opt)
        #print compl
        return compl

    def help_set(self, arg):
        if not arg:
            print self.do_set.__doc__
            return
        try:
            option = self.conf.options.getOption(arg)
            print "%s: %s" % (arg, option.doc)
        except KeyError:
            print "set: no such option: %s" % arg

    def do_rm(self, arg):
        """Remove password
        
Syntax:
    rm <regexp>
    
Remove password from database. If several passwords matches <regexp>, you will
be prompted to choose one from the list."""

        if not arg:
            print "rm: you must specify a password to remove"
            return

        selected_password = self.pickPassword(arg)
        if not selected_password:
            print "No password selected."
            return

        print selected_password.asText()
        answer = raw_input("Do you really want to delete this password (y/N)? ")
        if answer.lower().startswith('y'):
            # Do delete selected password
            self.getPwd().removeNode(selected_password)
            print "Password deleted"
            self.tryToSave()
        else:
            print "Password was not deleted."

    def mainLoop(self):
        self.updatePrompt()
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            self.do_exit("")

    def showMessage(self, message):
        print message
        

