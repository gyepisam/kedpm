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
# $Id: password_tree.py,v 1.2 2003/08/07 22:26:11 kedder Exp $

""" Password items organized in recursive tree """

import re

from kedpm.password import Password

class PasswordTree:
    _nodes = []
    _branches = {}
    
    def __init__(self):
        " Create named tree instance """
        self._nodes = []
        self._branches = {}

    def addNode(self, node):
        """ add node to the tree """
        self._nodes.append(node)

    def addBranch(self, name):
        """ add new branch to the tree """
        if self._branches.has_key(name):
            raise AttributeError, "Branch already exists"
        branch = PasswordTree()
        self._branches[name] = branch
        return branch

    def getNodes(self):
        """ return all non-tree nodes of the tree """
        return self._nodes

    def getBranches(self):
        """ return all branch nodes of the tree """
        return self._branches
   
    def get(self, branch, default=None):
        return self._branches.get(branch, default)
   
    def __getitem__(self, key):
        return self._branches[key]

    def locate(self, pattern):
        '''returns list of passwords, matching pattern'''
        re_search = re.compile(".*"+pattern+".*")
        results = []
        for password in self._nodes:
            for field in password.getSearhableFields():
                fval = getattr(password, field)
                if re_search.match(fval):
                    results.append(password)
                    break
        return results

    def getTreeFromPath(self, path):
        '''Return password tree from given path
        path is list of path items'''
        path = self.normalizePath(path)
        tree = self
        if path == []:
            return tree
        for pathitem in path:
            tree = tree[pathitem]
        return tree

    def normalizePath(self, path):
        '''reduce .. and . items from path
        path is list of path items'''
        normal = []
        for pathitem in path:
            if pathitem == ".":
                continue
            if pathitem == "..":
                normal = normal[:-1]
                continue
            normal.append(pathitem)
        return normal
        
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
