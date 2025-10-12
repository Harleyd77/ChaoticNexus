import os, sys

# Ensure we can import src/ package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from powder_app import main as m

print('BASE_DIR=', m.BASE_DIR)
print('STORAGE_DIR=', m.STORAGE_DIR)
print('DATA_DIR=', m.DATA_DIR)
print('DB_PATH=', m.DB_PATH)
print('TEMPLATES_DIR=', os.path.join(os.path.dirname(m.__file__), 'templates'))
print('STATIC_DIR=', os.path.join(os.path.dirname(m.__file__), 'static'))

