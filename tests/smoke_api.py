"""Quick API smoke test script."""
import requests
API = 'http://127.0.0.1:8000'

# Test GET endpoints
for ep in ['/health', '/attacks', '/thresholds', '/config', '/reality-check']:
    r = requests.get(API + ep)
    print(f'GET {ep}: {r.status_code}')

# Test simulate each attack
for attack in ['legitimate', 'blind_forgery', 'informed_forgery', 'replay',
               'impersonation', 'unauthorized_verifier', 'channel_manipulation']:
    r = requests.post(f'{API}/simulate/{attack}', params={'strength': 0.5})
    d = r.json()
    verdict = d['verdict']
    atype = d['attack_type']
    score = d['threat_score']
    print(f'POST /simulate/{attack}: {r.status_code} | verdict={verdict} | type={atype} | score={score}')

# History and audit
print(f'GET /history: {requests.get(API + "/history").status_code}')
av = requests.get(API + '/audit/verify').json()
print(f'GET /audit/verify: valid={av["valid"]}')

# Shor
r = requests.get(API + '/shor-toy')
factors = r.json()['factors_found']
print(f'GET /shor-toy: factors={factors}')

print('\nAll endpoints OK!')
