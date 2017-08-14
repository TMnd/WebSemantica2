#!"C:\Users\joaoa\Nextcloud\Documents\Universidade\Web Semântica\WebSemantica2\Trabalho2\Trabalho2\env\Scripts\python.exe"
# EASY-INSTALL-ENTRY-SCRIPT: 'rdfextras==0.4','console_scripts','csv2rdf'
__requires__ = 'rdfextras==0.4'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('rdfextras==0.4', 'console_scripts', 'csv2rdf')()
    )
