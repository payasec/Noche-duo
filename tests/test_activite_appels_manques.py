import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)+"/"; FIX=HERE+"/fixtures/"; MOCK=HERE+"/mock-firebase.js"
OUT=os.environ.get("ND_OUT","/tmp/nd-tests")+"/"; os.makedirs(OUT,exist_ok=True)
CHROME={"executable_path":os.environ["CHROME"]} if os.environ.get("CHROME") else {}
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(**CHROME,args=["--no-sandbox","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,permissions=["microphone","camera"])
    ctx.add_init_script(path=MOCK)
    A=ctx.new_page(); B=ctx.new_page()
    for pg,n in ((A,"Michel"),(B,"Nadia")):
        pg.on("pageerror",lambda e,n=n: errs.append(n+" "+str(e)+" @ "+(e.stack or "")[:600]))
        pg.goto("http://localhost:8771/"); pg.wait_for_timeout(300)
        pg.click('.langbig[data-lang="fr"]'); pg.click("#onb-next"); pg.fill("#onb-me",n); pg.click("#onb-next"); pg.click("#onb-later")
    A.click("#ol-create"); A.wait_for_timeout(300); code=A.inner_text("#ol-code-show")
    B.click("#ol-join"); B.fill("#ol-code",code); B.click("#ol-join-go"); B.wait_for_timeout(800)
    for pg in (A,B):
        if pg.is_visible("#moonx"): pg.click("#moonx")
    # B "leaves": close B page, A does actions
    B.click('.tabbar [data-tab="play"]'); A.wait_for_timeout(300)
    A.click("#ol-pulse"); A.wait_for_timeout(3200); A.click("#ol-hug"); A.wait_for_timeout(4200)
    A.click('.tabbar [data-tab="chat"]'); A.fill("#ch-input","Tu es où mon amour ?"); A.click("#ch-send"); A.wait_for_timeout(200)
    A.click('.tabbar [data-tab="together"]'); A.wait_for_timeout(200)
    A.click("#call-start"); A.wait_for_timeout(2000); A.click("#cb-end"); A.wait_for_timeout(800)
    print("A chat call bubble:", end=" "); A.click('.tabbar [data-tab="chat"]'); A.wait_for_timeout(300); print(A.inner_text(".msg.mine .callb").replace("\n"," | "))
    # B comes back
    B.evaluate("document.querySelectorAll('#toast').forEach(e=>e.classList.remove('show'))"); B.click('.tabbar [data-tab="home"]'); B.wait_for_timeout(800)
    print("B bell:",B.is_visible("#go-activity"),B.inner_text("#bell-n") if B.is_visible("#bell-n") else "-")
    print("B away card:",B.is_visible("#away-card"),"|",B.inner_text("#away-list").replace("\n"," | "))
    B.screenshot(path=OUT+"act_home.png")
    B.click("#go-activity"); B.wait_for_timeout(300)
    print("B activity:",B.inner_text("#act-list").replace("\n"," | ")[:400]); print("title:",B.inner_text("#hdr-title"))
    B.screenshot(path=OUT+"act_list.png")
    B.go_back(); B.wait_for_timeout(200); print("back to:",B.evaluate("[...document.querySelectorAll('.screen')].find(s=>!s.hidden).id"),"| bell count:",B.is_visible("#bell-n"))
    B.click('.tabbar [data-tab="chat"]'); B.wait_for_timeout(300)
    print("B chat call:",B.inner_text(".msg.theirs .callb").replace("\n"," | "))
    B.screenshot(path=OUT+"act_chat.png")
    B.click(".msg.theirs .callb .recall"); A.wait_for_timeout(1500); print("recall rings A:",A.is_visible("#cs-inc"))
    A.click("#cb-accept"); B.wait_for_timeout(3000); A.click("#cb-end"); B.wait_for_timeout(1000)
    print("B chat last:",B.inner_text(".msg.mine .callb").replace("\n"," | ") if B.query_selector(".msg.mine .callb") else "?")
    b.close()
print("ERRORS:",errs)
