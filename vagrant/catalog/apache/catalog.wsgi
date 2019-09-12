#!/usr/bin/python2.7

import logging
import sys

sys.stderr.write('\n'.join(sys.path))

output = u''
output += u'sys.version = %s\n' % repr(sys.version)
output += u'sys.prefix = %s\n' % repr(sys.prefix)

sys.stderr.write(output)

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/catalog')

from catalog import app as application
application.secret_key = 'super_secret_key'
