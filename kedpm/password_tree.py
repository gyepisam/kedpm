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
# $Id: password_tree.py,v 1.16 2004/02/28 18:45:20 kedder Exp $

"""Password items organized in recursive tree."""

import re

from password import Password
from exceptions import RenameError

class PasswordTreeIterator:
    def __init__(self, tree, parent=None):
        self.path = []
        self.tree = tree
        self.flat=self.buildFlatTree(tree) + [[]]
        self.tree_index=0
        self.pass_index=0

    def buildFlatTree(self, tree, path=[]):
        flat = []
        for name, subtree in tree.getBranches().items():
            flat.append(path+[name])
            flat += self.buildFlatTree(subtree, path+[name])
        return flat

    def getCurrentTree(self):
        return self.tree.getTreeFromPath(self.flat[self.tree_index])

    def getCurrentCategory(self):
        if self.tree_index >= len(self.flat):
            return None
        return self.flat[self.tree_index]

    def next(self):
        """This will iterate through whole password tree. next() method will
        consequently return every item in password tree.
        
        Return None if no more passwords exists."""
        if self.tree_index >= len(self.flat):
            return None

        while 1:
            curtree = self.getCurrentTree()
            if len(curtree.getNodes()) > self.pass_index:
                pwd = curtree.getNodes()[self.pass_index]
                self.pass_index += 1
                return pwd
            else:
                # next tree
                self.pass_index = 0
                self.tree_index += 1
                if self.tree_index >= len(self.flat):
                    return None
        return None
            
        
        

class _PasswordTreeIterator:
    def __init__(self, tree, parent=None):
        self.parent = None
        self.pass_index = 0
        self.branch_index = 0
        self.branches = tree.getBranches().keys()
        self.branches.sort()
        self.br_iterator = None
        self.stopped = 0
        self.tree = tree

    def getCurrentCategory(self):
        try:
            return self.branches[self.branch_index]
        except IndexError:
            return ""
        
    def next(self):
        """This will iterate through whole password tree. next() method will
        consequently return every item in password tree."""
        
        if len(self.branches) > self.branch_index or self.branch_index==-1:
            if self.br_iterator:
                nxt = self.br_iterator.next()
                if nxt:
                    return nxt
                self.branch_index += 1
                self.br_iterator = None
                return self.next()
            else:
                self.br_iterator = self.tree[self.branches[self.branch_index]].getIterator()
                return self.next()

        else:
            # iterate on passwords
            nodes = self.tree.getNodes()
            if len(nodes) > self.pass_index:
                pwd = nodes[self.pass_index]
                self.pass_index += 1
                return pwd
            else:
                return None


class PasswordTree:
    _nodes = []
    _branches = {}
    
    def __init__(self):
        """Create named tree instance."""
        self._nodes = []
        self._branches = {}

    def addNode(self, node):
        """Add node to the tree."""
        self._nodes.append(node)

    def addBranch(self, name):
        """Add new branch to the tree."""
        if self._branches.has_key(name):
            raise AttributeError, "Branch already exists"
        branch = PasswordTree()
        self._branches[name] = branch
        return branch

    def getNodes(self):
        """Return all non-tree nodes of the tree."""
        return self._nodes

    def getBranches(self):
        """Return all branch nodes of the tree."""
        return self._branches
   
    def get(self, branch, default=None):
        """Return branch if such exists, or default otherwise"""
        return self._branches.get(branch, default)
   
    def __getitem__(self, key):
        return self._branches[key]

    def locate(self, pattern):
        """Return list of passwords, matching pattern."""
        try:
            re_search = re.compile(".*"+pattern+".*", re.IGNORECASE)
        except re.error:
            re_search = re.compile(".*"+re.escape(pattern)+".*", re.IGNORECASE)
        results = []
        for password in self._nodes:
            for field in password.getSearhableFields():
                fval = getattr(password, field)
                if re_search.match(fval):
                    results.append(password)
                    break
        return results

    def getTreeFromPath(self, path):
        """Return password tree from given path.

        path is list of path items."""
        path = self.normalizePath(path)
        tree = self
        if path == []:
            return tree
        for pathitem in path:
            tree = tree[pathitem]
        return tree

    def renameBranch(self, path, newname):
        """Set new name for the given branch. Do not rename tree root - just
        leave it as is. Tree root don't have any name anyway."""
        path = self.normalizePath(path)
        if not path:
            return
        parent_tree = self.getTreeFromPath(path[:-1])
        oldname = path[-1]
        try:
            self.getTreeFromPath(path[:-1] + [newname])
        except KeyError:
            pass
        else:
            raise RenameError, "Category \"%s\" already exists." % newname
        branches = parent_tree.getBranches()
        cat = branches[oldname]
        del branches[oldname]
        branches[newname] = cat

    def normalizePath(self, path):
        """Reduce .. and . items from path.

        path is list of path items."""
        normal = []
        for pathitem in path:
            if pathitem == "." or pathitem == "":
                continue
            if pathitem == "..":
                normal = normal[:-1]
                continue            
            normal.append(pathitem)
        return normal
    
    def getIterator(self):
        return PasswordTreeIterator(self)

    def flatten(self):
        """Traverse the whole tree and return flat representation of it as
        PasswordTree instance."""

        result = PasswordTree()
        iter = self.getIterator()
        while 1:
            pwd = iter.next()
            if pwd is None:
                break
            result.addNode(pwd)
        return result
    
    def asString(self, indent = 0):
        output = ""
        indstr = " " * (indent*4)
        for (bname, branch) in self._branches.items():
            output = output + indstr + bname+"\n"
            output = output + branch.asString(indent+1)
        for password in self._nodes:
            output = output + indstr + str(password) + "\n"
        return output

    def __str__(self):
        return self.asString()

    def getBranchContainingNode(self, node):
        if node in self._nodes:
            return self
        for branch in self._branches.values():
            res = branch.getBranchContainingNode(node)
            if res:
                return res
        else:
            return None

    def removeNode(self, node):
        """Removes a node from the tree.
        
        If node is not found in the current branch, search for node recursively
        in whole subtree."""
        container = self.getBranchContainingNode(node)
        container._nodes.remove(node)

    def removeBranch(self, name):
        """Removes a branch from the tree."""
        del(self._branches[name])
