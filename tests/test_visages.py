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
        pg.on("pageerror",lambda e,n=n: errs.append(n+" "+str(e)))
        pg.goto("http://localhost:8771/"); pg.wait_for_timeout(300)
        pg.click('.langbig[data-lang="fr"]'); pg.click("#onb-next"); pg.fill("#onb-me",n); pg.click("#onb-next"); pg.click("#onb-later")
    A.click("#ol-create"); A.wait_for_timeout(300); code=A.inner_text("#ol-code-show")
    B.click("#ol-join"); B.fill("#ol-code",code); B.click("#ol-join-go"); B.wait_for_timeout(800)
    for pg in (A,B):
        if pg.is_visible("#moonx"): pg.click("#moonx")
    A.click('#go-settings'); A.wait_for_timeout(300)
    A.evaluate("document.getElementById('faces-card').closest('details').open=true")
    A.set_input_files("#in-face-me",FIX+"visage-a.jpg"); A.set_input_files("#in-face-love",FIX+"visage-b.jpg"); A.wait_for_timeout(800)
    A.locator("#faces-card").screenshot(path=OUT+"faces_card.png")
    B.click('.tabbar [data-tab="chat"]'); B.wait_for_timeout(500)
    print("B chat head photo:",B.is_visible("#ch-photo"))
    A.go_back(); A.wait_for_timeout(200); A.click('.tabbar [data-tab="chat"]'); A.wait_for_timeout(200)
    A.click("#ch-hug"); B.wait_for_timeout(1900); B.screenshot(path=OUT+"faces_hug.png")
    B.click("#hug-close"); A.wait_for_timeout(4000)
    A.click('.tabbar [data-tab="together"]'); A.wait_for_timeout(200); A.click("#call-start"); B.wait_for_timeout(1500); B.screenshot(path=OUT+"faces_call.png")
    B.click("#cs-decline"); A.wait_for_timeout(800)
    b.close()
print("ERRORS:",errs)
