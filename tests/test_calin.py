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
    for pg,n in ((A,"Jean"),(B,"Nadia")):
        pg.on("pageerror",lambda e,n=n: errs.append(n+" "+str(e)))
        pg.goto("http://localhost:8771/"); pg.wait_for_timeout(300)
        pg.click('.langbig[data-lang="fr"]'); pg.click("#onb-next"); pg.fill("#onb-me",n); pg.click("#onb-next"); pg.click("#onb-later")
    A.click("#ol-create"); A.wait_for_timeout(300); code=A.inner_text("#ol-code-show")
    B.click("#ol-join"); B.fill("#ol-code",code); B.click("#ol-join-go"); B.wait_for_timeout(800)
    for pg in (A,B):
        if pg.is_visible("#moonx"): pg.click("#moonx")
    A.click('.tabbar [data-tab="chat"]'); A.wait_for_timeout(200)
    print("hug button:",A.inner_text("#ch-hug"))
    A.click("#ch-hug"); A.wait_for_timeout(500); print("A sent overlay:",A.inner_text("#hug-t"))
    B.wait_for_timeout(1700); print("B overlay:",B.is_visible("#hugfx"),B.inner_text("#hug-t"),"| back btn:",B.inner_text("#hug-back"))
    B.screenshot(path=OUT+"hug_B_noimg.png")
    B.click("#hug-back"); A.wait_for_timeout(4500)
    print("A got back:",A.inner_text("#hug-t"),"| badge:", "hug" in A.evaluate("JSON.parse(localStorage.getItem('nd-profile')).badges"))
    A.click("#hug-close"); A.wait_for_timeout(300)
    # upload hug photo on A via settings
    A.click('#go-settings')
    A.wait_for_timeout(300); A.set_input_files("#in-hug",FIX+"couple-test.jpg"); A.wait_for_timeout(1200)
    print("A preview overlay:",A.is_visible("#hugfx"),"| settings img:",A.is_visible("#set-hug"))
    B.wait_for_timeout(500); print("B got hug photo:",B.evaluate("!!localStorage.getItem('nd-hug')"))
    A.wait_for_timeout(5000)
    A.go_back(); A.wait_for_timeout(300); A.click('.tabbar [data-tab="chat"]'); A.wait_for_timeout(300)
    A.click("#ch-hug"); B.wait_for_timeout(2300); B.screenshot(path=OUT+"hug_B_img.png")
    B.click("#hug-close"); B.click('.tabbar [data-tab="chat"]'); B.wait_for_timeout(400); B.screenshot(path=OUT+"hug_B_chat.png")
    b.close()
print("ERRORS:",errs)
