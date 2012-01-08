# -*- coding: utf-8 -*-
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
