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
# $Id: test_parser.py,v 1.6 2003/10/25 17:21:50 kedder Exp $

import unittest

from kedpm import parser

class ParserTestCase(unittest.TestCase):
    
    pattern = '(^|.*\s)Username/Password: (?P<user>.*?)/(?P<password>.*?)($|\s)'
    cases = [
        {"text": 'Username/Password: actualusername/actualpassword',
        "match": {'password': 'actualpassword', 'user': 'actualusername'}},
        
        {"text": '''This is a first line
        Username/Password: longusername/longpassword  asd
        Some other line''',
        "match": {'password': 'longpassword', 'user': 'longusername'}},

        {"text": 'USERNAME/PASSWORD: the username/!@#%^^&*(',
        "match": {'password': '!@#%^^&*(', 'user': 'the username'}},
    ]

    ml_pattern = '''^
    Username: (?P<user>.*?)
    Password: (?P<password>.*?)
(?P<description>.*?)
$'''
    ml_cases = [
        {"text": '''
    Username: mlusername
    Password: mlpassword

''',
        "match": {'password': 'mlpassword', 'user': 'mlusername'}},

        {"text": '''
    Username: 
    Password: mlpassword2
    
    This is a multiline 
    description
''',

        "match": {'password': 'mlpassword2', 'description': '''This is a multiline 
    description'''}}
    ]
    
    def test_parse(self):
        for pattern, cases in [(self.pattern, self.cases), (self.ml_pattern, self.ml_cases)]:
            for case in cases:
                match = parser.parse(pattern, case["text"])
                self.assertEqual(match, case["match"])

    def test_regularize(self):
        cases = [
            ("{~.*}", "(^|.*\s).*($|\s)"),
            ("{~test.+}", '(^|.*\s)test.+($|\s)'),

            ("{the}{test}", '(^|.*\s)(?P<the>.*?)(?P<test>.*?)($|\s)'),
            ("""{hello}
            {~(test)+}
            {}
            {welcome}
            """,
            """(^|.*\s)(?P<hello>.*?)
            (test)+
            .*
            (?P<welcome>.*?)
            ($|\s)"""),
        ]
        for pattern, regexp in cases:
            res = parser.regularize(pattern)
            self.assertEqual(res, regexp)
       
    def test_parser(self):
        pattern = "Username/Password: {user}/{password}"
        expr = parser.regularize(pattern)
        for case in self.cases:
            match = parser.parse(expr, case["text"])
            self.assertEqual(match, case["match"])

    def test_parseMessage(self):
        texts = ["username/password: actualuser/actualpassword",
        """Username : actualuser
        Password    : actualpassword""",
        "user: actualuser pass:actualpassword"
        ]
        result = {'password': 'actualpassword', 'user': 'actualuser'}
        for text in texts:
            dict = parser.parseMessage(text, parser.patterns)
            self.assertEqual(dict, result)
            

def suite():
    return unittest.makeSuite(ParserTestCase, 'test')

if __name__ == "__main__":
    unittest.main()
