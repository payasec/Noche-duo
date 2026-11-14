import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)+"/"; FIX=HERE+"/fixtures/"; MOCK=HERE+"/mock-firebase.js"
OUT=os.environ.get("ND_OUT","/tmp/nd-tests")+"/"; os.makedirs(OUT,exist_ok=True)
CHROME={"executable_path":os.environ["CHROME"]} if os.environ.get("CHROME") else {}
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(**CHROME,args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2)
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
    A.wait_for_timeout(500); A.locator("#online-card").screenshot(path=OUT+"home_hug.png")
    A.click("#ol-hug"); B.wait_for_timeout(1500); print("B hug:",B.is_visible("#hugfx"),B.inner_text("#hug-t"))
    b.close()
print("ERRORS:",errs)
