# -*- coding: utf-8 -*-

#    XMPPVOX: XMPP client for DOSVOX.
#    Copyright (C) 2012  Rodolfo Henrique Carvalho
#
#    This file is part of XMPPVOX.
#
#    XMPPVOX is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

raise SystemExit(u"""
    setup.py não deve ser usado no momento.
    Ao invés de usar o py2exe, use o PyInstaller
    através do script build.bat.
""")

from distutils.core import setup
import py2exe

setup(
    version = '0.1.0',
    name = 'XMPPVOX',
    description = 'XMPPVOX',

    console = ['xmppvox.py'],
    options = {
        'py2exe': {
            'bundle_files': 1,
            'compressed': True,
            'packages': [
                'dns',
                'sleekxmpp',
            ],
            'includes': [
                #'sleekxmpp.features.feature_starttls',
                #'sleekxmpp.features.feature_bind',
                #'sleekxmpp.features.feature_session',
                #'sleekxmpp.features.feature_mechanisms',
                #'sleekxmpp.plugins.base',
                #'sleekxmpp.plugins.xep_0030',
                #'sleekxmpp.plugins.xep_0004',
                #'sleekxmpp.plugins.xep_0060',
                #'sleekxmpp.plugins.xep_0199',
                'xml.etree.ElementTree',
            ],
            'excludes': [
                'calendar',
                'difflib',
                'doctest',
                'inspect',
                'locale',
                'pdb',
                'pickle',
                'pyreadline',
                'unittest',
            ],
        },
    },
    zipfile = None,
)
