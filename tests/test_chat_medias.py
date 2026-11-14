import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)+"/"; FIX=HERE+"/fixtures/"; MOCK=HERE+"/mock-firebase.js"
OUT=os.environ.get("ND_OUT","/tmp/nd-tests")+"/"; os.makedirs(OUT,exist_ok=True)
CHROME={"executable_path":os.environ["CHROME"]} if os.environ.get("CHROME") else {}
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(**CHROME,args=["--no-sandbox","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=1,permissions=["microphone","camera"])
    ctx.add_init_script(path=MOCK)
    A=ctx.new_page(); B=ctx.new_page()
    for pg,n in ((A,"Michel"),(B,"Nadia")):
        pg.on("pageerror",lambda e,n=n: errs.append(n+" "+str(e)))
        pg.goto("http://localhost:8771/"); pg.wait_for_timeout(300)
        pg.click('.langbig[data-lang="fr"]'); pg.click("#onb-next"); pg.fill("#onb-me",n); pg.click("#onb-next"); pg.click("#onb-later")
    A.click("#ol-create"); A.wait_for_timeout(300); code=A.inner_text("#ol-code-show")
    B.click("#ol-join"); B.fill("#ol-code",code); B.click("#ol-join-go"); B.wait_for_timeout(800)
    for pg in (A,B):
        if pg.is_visible("#moonx"): pg.click("#moonx")
        pg.click('.tabbar [data-tab="chat"]'); pg.wait_for_timeout(150)
    # legacy inline photo message written the old way must still show
    A.evaluate("""()=>{var c=JSON.parse(localStorage.getItem('nd-profile')).couple.code;var cv=document.createElement('canvas');cv.width=40;cv.height=40;var x=cv.getContext('2d');x.fillStyle='#f0c674';x.fillRect(0,0,40,40);
      return firebase.database().ref('couples/'+c+'/live/chat/m00000000000001aaaa').set({from:'a',at:1,img:cv.toDataURL('image/jpeg')});}""")
    A.wait_for_timeout(300)
    print("legacy photo visible on B:",B.is_visible(".msg.theirs .bubble img"))
    # new photo
    A.set_input_files("#ch-file",ROOT+"icon-512.png"); B.wait_for_timeout(1200)
    st=B.evaluate("""()=>{var c=JSON.parse(localStorage.getItem('nd-profile')).couple.code;return firebase.database().ref('couples/'+c+'/live/chat').once('value').then(s=>{var v=s.val();var last=v[Object.keys(v).sort().pop()];return {hasInline:!!last.img,mid:last.mid,mk:last.mk,size:JSON.stringify(last).length};});}""")
    print("new message stored:",st)
    print("B photo shown:",B.locator(".msg.theirs .bubble img").count())
    # voice note
    A.click("#ch-mic"); A.wait_for_timeout(1500); A.click("#ch-send"); B.wait_for_timeout(1500)
    print("B voice button:",B.inner_text(".msg.theirs .vplay") if B.query_selector(".msg.theirs .vplay") else "none")
    B.click(".msg.theirs .vplay"); B.wait_for_timeout(800); print("B audio loaded on tap:",B.locator(".msg.theirs audio").count())
    # preview in toast/feed text + delete removes media
    mid=st["mid"]
    A.click('.msg.mine .bubble >> nth=0', button="right"); A.wait_for_timeout(200)
    # many messages -> older button
    for i in range(65):
        A.evaluate("""(i)=>{var c=JSON.parse(localStorage.getItem('nd-profile')).couple.code;return firebase.database().ref('couples/'+c+'/live/chat/m'+String(Date.now()+i).padStart(14,'0')+'zz'+i).set({from:'a',at:Date.now(),t:'msg '+i});}""", i)
    B.wait_for_timeout(1200)
    n1=B.locator("#chat-list .msg").count(); print("B messages shown:",n1,"| older button:",B.is_visible(".older-btn"))
    B.click(".older-btn"); B.wait_for_timeout(1000); print("after older:",B.locator("#chat-list .msg").count(),"| hug overlay replayed by mistake:",B.is_visible("#hugfx"))
    print("phone cache entries on B:",B.evaluate("()=>new Promise(r=>{var q=indexedDB.open('nd-media',1);q.onsuccess=()=>{var c=q.result.transaction('m').objectStore('m').count();c.onsuccess=()=>r(c.result);};q.onerror=()=>r(-1);})"))
    # cache: reload B page media from IndexedDB without network fetch counting
    b.close()
print("ERRORS:",errs)
