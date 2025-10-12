import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from powder_app import main as m

rules = list(m.app.url_map.iter_rules())
endpoints = sorted({r.endpoint for r in rules})
print({'route_count': len(rules), 'endpoints_sample': endpoints[:15]})

