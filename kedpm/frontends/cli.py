# Copyright (C) 2003-2005  Andrey Lebedev <andrey@micro.lt>
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
# $Id: cli.py,v 1.37 2006/02/13 05:04:07 anarcat Exp $

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
from os.path import expanduser
import readline

class Application (Cmd, Frontend):
    PS1 = "kedpm:%s> " # prompt template
    cwd = []  # Current working directory
    intro = _("""Ked Password Manager is ready for operation.
try 'help' for brief description of available commands.
""")

    modified = 0
    histfile = os.getenv("HOME") + '/.kedpm/history'

    def __init__(self):
        Cmd.__init__(self)
        if sys.stdout.isatty():
            self.PS1 = "\x1b[1m"+self.PS1+"\x1b[0m" # colored prompt template


    def printMessage(self, message, *vars):
        if self.verbose:
          print (message) % vars

    def openDatabase(self):
        ''' Open database amd prompt for password if necessary '''
        
        self.verbose = self.conf.options['verbose']
        self.force_single = self.conf.options['force-single']
        self.confirm_deletes = self.conf.options['confirm-deletes']

        self.pdb = PDBFigaro(filename = expanduser(self.conf.options['fpm-database']))
        password = ""
        self.printMessage(_("Ked Password Manager (version %s)"), __version__)

        while 1:
            try:
                self.pdb.open(password)
                break
            except WrongPassword:
                if password:
                    print _("Error! Wrong password.")
                else:
                    print _("Provide password to access the database (Ctrl-C to exit)")
                password = getpass(_("Password: "))
            except DatabaseNotExist:
                password = self.createNewDatabase()
        self.printMessage(_("Password accepted."))
        print

    def createNewDatabase(self):
        'Create new password database and return password for created database'
        print _("Creating new password database.")
        pass1 = pass2 = ""
        while pass1 != pass2 or pass1 == "":
            pass1 = getpass(_("Provide password: "))
            pass2 = getpass(_("Repeat password: "))
            if pass1 == '':
                print _("Empty passwords are really insecure. You should " \
                        "create one.")
            if pass1!=pass2:
                print _("Passwords don't match! Please repeat.")

        self.pdb.create(pass1)
        return pass1

    def updatePrompt(self):
        self.prompt = self.PS1 % ('/'+'/'.join(self.cwd))

    def getCwd(self):
        'Return current working password tree instance'
        return self.pdb.getTree().getTreeFromPath(self.cwd)

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

    def filterPasswords(self, regexp, tree = None):
      '''Returns a list of passwords, filtered by REGEXP'''
      if tree is None:
            tree = self.getCwd()
      
      return(tree.locate(regexp))


    def getPasswords(self, regexp, tree = None):
      '''Returns a list of passwords, filtered by REGEXP.
         Calls pickPassword if program has been configured to force
         single selection'''
      
      if self.force_single:
            return [self.pickPassword(regexp, tree)] 
      else:
            return(self.filterPasswords(regexp, tree))
         
    def pickPassword(self, regexp, tree = None):
        '''Prompt user to pick one password from given password tree. Password
        tree, provided by "tree" argument filtered using "regexp".

        If resulted list contains only one password, return it without
        prompting. If no passwords were located, or user desides to cancel
        operation, return None'''

        passwords = self.filterPasswords(regexp, tree)
        
        if not passwords:
            self.printMessage(_("No passwords matching \"%s\" were found"), regexp)
            return None
          
         
        if len(passwords) > 1:
            self.listPasswords(passwords, 1)
            print _("Enter number. Enter 0 to cancel.")
            try:
                showstr = raw_input(_('show: '))
            except (KeyboardInterrupt, EOFError):
                # user has cancelled selection
                showstr = "0"
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
                print _("Passwords don't match. Try again.")
        return pwd

    def editPassword(self, pwd):
        '''Prompt user for each field of the password. Respect fields' type.'''

        input = {}

        for field, fieldinfo in pwd.fields_type_info:
            field_type = fieldinfo['type']

            new_value = ""
            if field_type == password.TYPE_STRING:
                new_value = self.inputString(_("Enter %s (\"%s\"): ") % (pwd.getFieldTitle(field), pwd[field]))
            elif field_type == password.TYPE_TEXT:
                new_value = self.inputText(_("Enter %s (\"%s\"): ") % (pwd.getFieldTitle(field), pwd[field]))
            elif field_type == password.TYPE_PASSWORD:
                new_value = self.inputPassword(_("Enter %s: ") % pwd.getFieldTitle(field))
            else:
                print _("Error. Type %s is unsupported yet. " \
                        "This field will retain an old value.") % field_type

            if new_value!="":
                input[field] = new_value

        try:
            pwd.update(input)
        except FigaroPasswordTooLongError:
            print _("WARNING! Your password is too long for Figaro Password Manager.")
            print _("Figaro Password Manager can handle only passwords shorter than 24 characters.")
            print _("""However, KedPM can store this password for you, but it
will break fpm compatibility. fpm will not be able to handle such
long password correctly.""")
            answer = raw_input(_("Do you still want to save your password? [Y/n]: "))
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
            answer = raw_input(_("Database was modified. Do you want to save it now? [Y/n]: "))
        if answer=='' or answer.lower().startswith('y'):
            self.do_save('')

    def complete_dirs(self, text, line, begidx, endidx):
        completing = line[:endidx].split(' ')[-1]
        base = completing[:completing.rfind('/')+1]
        abspath = self.getAbsolutePath(base)
        dirs = self.pdb.getTree().getTreeFromPath(abspath).getBranches()
        compl = []
        for dir in dirs.keys():
            if dir.startswith(text):
                compl.append(dir+'/')
        return compl

    def getEditorInput(self, content=''):
        """Fire up default editor and read user input from temporary file"""
        default_editor = "vi"
        if os.environ.has_key('VISUAL'):
            editor = os.environ['VISUAL']
        elif os.environ.has_key('EDITOR'):
            editor = os.environ['EDITOR']
        else:
            editor = default_editor
        self.printMessage(_("running %s"), editor)
        # create temporary file
        handle, tmpfname = tempfile.mkstemp(prefix="kedpm_")
        tmpfile = open(tmpfname, 'w')
        tmpfile.write(content)
        tmpfile.close()
        
        os.system(editor + " " + tmpfname)

        tmpfile = open(tmpfname, 'r')
        text = tmpfile.read()
        tmpfile.close()
        os.remove(tmpfname)
        return text

    def getAbsolutePath(self, arg):
        """Return absolute path from potentially relative (cat)"""
        root = self.pdb.getTree()
        if not arg:
            return self.cwd
        if(arg[0] == '/'):
            path = root.normalizePath(arg.split('/'))
        else:
            path = root.normalizePath(self.cwd + arg.split('/'))
        return path

    def getTreeFromRelativePath(self, path):
        """Get tree object from given relative path and current working
        directory"""
        root = self.pdb.getTree()
        abspath = self.getAbsolutePath(path)
        return root.getTreeFromPath(abspath)

    ##########################################
    # Command implementations below.         #

    def emptyline(self):
        pass

    def do_exit(self, arg):
        '''Quit KED Password Manager'''
        readline.write_history_file(self.histfile)
        if self.modified:
            self.tryToSave()
        self.printMessage(_("Exiting."))
        sys.exit(0)

    def do_EOF(self, arg):
        '''The same as 'exit' command'''
        print
        self.do_exit(arg)

    def do_quit(self, arg):
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
        try:
            tree = self.getTreeFromRelativePath(arg)
        except KeyError:
            print _("ls: %s:  No such catalog") % arg
            return
        
        print _("=== Directories ===")
        for bname in tree.getBranches().keys():
            print bname+"/"
        print _("==== Passwords ====")
        self.listPasswords(tree.getNodes())

    def complete_ls(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)

    def do_cd(self, arg):
        '''change directory (category)

Syntax:
    cd <category>
'''
        root = self.pdb.getTree()
        cdpath = self.getAbsolutePath(arg)
        try:
            newpath = root.getTreeFromPath(cdpath)
        except KeyError:
            print _("cd: %s: No such catalog") % arg
        else:
            self.cwd = cdpath
            self.updatePrompt()

    def complete_cd(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)

    def do_pwd(self, arg):
        '''print name of current/working directory'''
        print '/'+'/'.join(self.cwd)

    def do_show(self, arg):
        '''display password information.

Syntax:
    show [-r] <regexp>

    -r - recursive search. search all subtree for matching passwords

This will display contents of a password item in current category or whole
subtree, if -r flag was specified. If several items matched by <regexp> and the
program has been configured to prompt for a single entry, a list
of them will be printed and you will be prompted to enter a number, pointing to
password you want to look at.  After receiving that number, KedPM will show you
the password. Otherwise all matching entries will be displayed'''

        argv = arg.split()
        tree = None
        if argv and argv[0] == '-r':
            tree = self.getCwd().flatten()
            if len(argv) > 1:
                arg = " ".join(argv[1:])
            else:
                arg = ""

        selected_passwords = self.getPasswords(arg, tree)
        for record in selected_passwords:
            print "---------------------------------------"
            print record.asText()
            print "---------------------------------------"

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
                self.printMessage(_("Cancelled"))
        else:
            self.printMessage(_("No password selected"))

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
            choosendict = parser.parseMessage(text, self.conf.patterns)
            new_pass.update(choosendict)

        try:
            self.editPassword(new_pass)
        except (KeyboardInterrupt, EOFError):
            self.printMessage(_("Cancelled"))
        else:
            tree = self.getCwd()
            tree.addNode(new_pass)
            self.tryToSave()

    def do_import(self, arg):
        '''Imports new password records into current category.
Syntax:
    import
    
    Get properties by parsing provided text. Will open default text editor
    for you to paste text in.
'''
        argv = arg.split()
        tree = self.getCwd()

        text = self.getEditorInput()
        for line in text.split("\n"):
          new_pass = FigaroPassword() # FIXME: Password type shouldn't be hardcoded.
          choosendict = parser.parseMessage(line, self.conf.patterns)
          new_pass.update(choosendict)
          tree.addNode(new_pass)

        self.tryToSave()

    def do_save(self, arg):
        '''Save current password tree'''
        sys.stdout.write(_("Saving..."))
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
            print _("mkdir: too few arguments")
            print _("try 'help mkdir' for more information")
            return

        pwd = self.getCwd()
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
            self.pdb.getTree().renameBranch(self.cwd+[oldname], newname)
        except RenameError:
            print _("rename: category %s already exists") % newname
            return
        except KeyError:
            print _("rename: %s: no such category") % oldname
            return
        self.tryToSave()

    def complete_rename(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)

    def do_passwd(self, arg):
        """Change master password for opened database
        
Syntax:
    password [new password]

If new password is not provided with command, you will be promted to enter new
one.
"""

        if not arg:
            # Password is not provided with command. Ask user for it
            pass1 = getpass(_("New password: "))
            pass2 = getpass(_("Repeat password: "))
            if pass1 == '':
                print _("Empty passwords are really insecure. You should " \
                        "create one.")
                return
            if pass1!=pass2:
                print _("Passwords don't match! Please repeat.")
                return
            new_pass = pass1
        else:
            new_pass = arg

        self.pdb.changePassword(new_pass)
        self.printMessage(_("Password changed."))
        

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
            print _("set: no such option: %s") % arg
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
        for opt in self.conf.options.keys():
            if opt.startswith(text):
                compl.append(opt)
        return compl

    def help_set(self, arg):
        if not arg:
            print self.do_set.__doc__
            return
        try:
            option = self.conf.options.getOption(arg)
            print "%s: %s" % (arg, option.doc)
        except KeyError:
            print _("set: no such option: %s") % arg

    def do_rm(self, arg):
        """Remove password

Syntax:
    rm <regexp>

Remove password from database. If several passwords matches <regexp> and the
'force-single' option is enabled, you will be prompted to select one from the
list. Otherwise all matching records will be selected.  If the
'confirm-deletes' option is enabled, you will be prompted to confirm the
deletion.  Otherwise records will be deleted without confirmation."""

        if not arg:
            print "rm: you must specify a password to remove"
            return

        selected_passwords = self.pickPassword(arg)
        if not selected_passwords:
            self.printMessage(_("No password selected."))
            return

        Cwd = self.getCwd()
        
        for password in selected_passwords:
            if self.confirm_deletes:
                print selected_password.asText()
                answer = raw_input("Do you really want to delete this " \
                                   "password (y/N)? ")
                if not answer.lower().startswith('y'):
                    self.printMessage(_("Password was not deleted."))
                    continue

            # Do delete selected password
            Cwd.removeNode(password)
            self.printMessage(_("Password deleted"))

            self.tryToSave()


    def do_mv(self, arg):
        '''move a password
Syntax:
    mv <regexp> <category>

Move a password record to a different category. If several records match, and the 'force-single' option
is enabled, you will be prompted to pick one. Otherwise all matching records will be moved.
'''
        args = arg.split()
        if len(args) != 2:
            print '''Syntax:
            mv <regexp> <category>
'''
            return

        pw = args[0]
        cat = args[1]

        # get destination category branch
        root = self.pdb.getTree()
        cat_path = self.getAbsolutePath(cat)
        try:
            dst_branch = root.getTreeFromPath(cat_path)
        except KeyError:
            print _("mv: %s: No such catalog") % cat
            return

        # select password from user
        selected_passwords = self.getPasswords(pw)
        if not selected_passwords:
            self.printMessage(_("No password selected"))
            return
          
        Cwd = self.getCwd

        for password in selected_passwords:
            dst_branch.addNode(password)
            Cwd().removeNode(password)
            self.tryToSave()

    def do_rmdir(self, arg):
        '''Delete a category (directory)

Syntax:
    rmdir <category>

Deletes a password category and ALL it\'s entries
'''
        if not arg:
            print _("rmdir: too few arguments")
            print _("try 'help rmdir' for more information")
            return

        abspath = self.getAbsolutePath(arg)
        if not abspath:
            print _("rmdir: Can't remove root directory")
            return
        pwd = self.pdb.getTree().getTreeFromPath(abspath[:-1])
        toremove = abspath[-1]
        abspath_str = '/'+'/'.join(abspath)
        
        #pwd = self.getCwd()
        answer = raw_input(_("Are you sure you want to delete category %s'" \
                " and ALL it's entries? [y/N]: ") % abspath_str)
        if answer.lower().startswith('y'):
            pwd.removeBranch(toremove)
            print _("rmdir: category \"%s\" and all it's entries were deleted.") % abspath_str
            self.tryToSave()

        # Check if current directory still exists. If not - cd to root.
        try:
            cwd = self.getCwd()
        except KeyError:
            print _("rmdir: Warning! Current working directory was removed. " \
                    "Changing to /")
            self.cwd = []
            self.updatePrompt()

    def complete_rmdir(self, text, line, begidx, endidx):
        return self.complete_dirs(text, line, begidx, endidx)

    def do_patterns(self, arg):
        '''Edit pareser patterns. Will open default text editor in order to
edit.'''

        disclaimer = '''# Here you can teach Ked Password Manager how to
# extract useful password information from your emails. For more
# information on format of these patterns please refer to KedPM
# documentation.
#
# Basic rules are:
#  {field} - matches password field;
#  { } - matches arbitrary number of spaces or nothing;
#  {~regexp} - matches arbitrary regular expression;
# 
# One line is one pattern. Empty lines and Lines starting with simbol "#" will
# be ignored.

'''

        pattern_text = '\n'.join(self.conf.patterns)
        text = self.getEditorInput(disclaimer+pattern_text)
        cr = '\n' # XXX This is possible unixism
        patterns = []
        for line in text.split(cr):
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            patterns.append(line)
        self.conf.patterns = patterns
        self.conf.save()

    def mainLoop(self):
        if os.access(self.histfile, os.R_OK):
            readline.read_history_file(self.histfile)
        self.updatePrompt()
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            self.do_exit("")

    def showMessage(self, message):
        print message

    def do_export(self, arg):
    	'''Export many passwords.

Syntax:
    export [-r] [<regexp> [<file> [<format]]]

    -r - recursive search. search all subtree for matching passwords
    <regexp> - match only those passwords
    <file> - export to file
    <format> - one of "plain" or "csv"

This will export the contents of matching passwords in the current directory or the whole subtree, if -r was specified. If <file> is not specified, the passwords are printed on stdout. Note that <file> will be overwritten if it exists.
'''

        argv = arg.split()
        tree = None
        regexp = ""
        if argv and argv[0] == '-r':
            tree = self.getCwd().flatten()
            argv = argv[1:]
        if len(argv) > 0:
            regexp = argv[0]

	selected_passwords = self.filterPasswords(regexp, tree)
        if len(argv) > 1:
            output = open(argv[1], 'w')
        else:
            output = sys.stdout
        for record in selected_passwords:
            if (len(argv) > 2) and (argv[2] == "csv"):
                output.write(record.asCSV())
            else:
                output.write(record.asText())
        if len(argv) > 1:
            output.close()
