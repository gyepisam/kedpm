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
# $Id: parser.py,v 1.7 2004/02/29 11:45:48 kedder Exp $

"""Password pattern functions.

Recognized patterns are::
    
    {field} - matches password field;
    { } - matches arbitrary number of spaces or nothing;
    {~regexp} - matches arbitrary regular expression;"""

import re

patterns = [
    "User{~(name)?}/Pass{~(word)?}{ }:{ }{user}/{password}",
    "User{~(name)?}{ }:{ }{user}",
    "Pass{~(word)?}{ }:{ }{password}",
    "Host{~(name)?}{ }:{ }{url}",
    "Server{ }:{ }{url}"
]

def parse(pattern, text):
    """Parse password text using regular expression

    Return dictionary of password properties.
    """
    match = re.match(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    if match is None:
        return {}
    groupdict = match.groupdict()
    for group, value in groupdict.items():
        if value.strip()=="":
            pass
            del groupdict[group]
        else:
            groupdict[group] = groupdict[group].strip()

    return groupdict

def regularize(pattern):
    """Return valid regular expression from password pattern

    Syntax:

    Property field::
        {name} => (?P<name>.*?)

    Arbitrary text::
        {} => .*

    Spaces::
        { } => \s*

    Custom regular expression::
        {~expr} => expr
    """

    expr = re.sub(r"\{~(.*?)\}", r"\1", pattern)
    expr = re.sub(r"\{\}", r".*", expr)
    expr = re.sub(r"\{ \}", r"\s*", expr)
    expr = re.sub(r"\{(\S*?)\}", r"(?P<\1>.*?)", expr)
    #return expr
    return "(^|.*\s)"+expr+"($|\s)"

def parseMessage(text, patterns = patterns):
    """Extract valuable password information from text and return filled
    password and return dictionary with gathered information."""

    choosendict = {}
    for pattern in patterns:
        regexp = regularize(pattern)
        passdict = parse(regexp, text)
        choosendict.update(passdict)

    return choosendict
