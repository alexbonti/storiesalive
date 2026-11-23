import json, os, mimetypes, urllib.request, sys
root=os.path.dirname(os.path.abspath(__file__))
files=['index.html','storia.json','vendor/leaflet.js','vendor/leaflet.css']
ct={'html':'text/html; charset=utf-8','json':'application/json','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}
meta=[{'path':p,'size':os.path.getsize(f'{root}/{p}'),'contentType':ct[p.rsplit('.',1)[1]]} for p in files]
H={'content-type':'application/json','X-HereNow-Client':'claude-code/frascati-game'}
r=urllib.request.Request('https://here.now/api/v1/publish',data=json.dumps({'files':meta}).encode(),headers=H,method='POST')
res=json.load(urllib.request.urlopen(r,timeout=30))
json.dump(res,open('risultato_publish.json','w'))
print('siteUrl',res.get('siteUrl'),'claimUrl',res.get('claimUrl'))
for u in res['upload']['uploads']:
    m=next(x for x in meta if x['path']==u['path'])
    rq=urllib.request.Request(u['url'],data=open(f"{root}/{u['path']}",'rb').read(),method='PUT',headers={**u.get('headers',{}),'Content-Type':m['contentType']})
    urllib.request.urlopen(rq,timeout=60); print('up',u['path'])
f=urllib.request.Request(res['upload']['finalizeUrl'],data=json.dumps({'versionId':res['upload']['versionId']}).encode(),headers=H,method='POST')
print(urllib.request.urlopen(f,timeout=30).read().decode())
