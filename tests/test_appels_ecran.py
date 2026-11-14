import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)+"/"; FIX=HERE+"/fixtures/"; MOCK=HERE+"/mock-firebase.js"
OUT=os.environ.get("ND_OUT","/tmp/nd-tests")+"/"; os.makedirs(OUT,exist_ok=True)
CHROME={"executable_path":os.environ["CHROME"]} if os.environ.get("CHROME") else {}
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(**CHROME,args=["--no-sandbox","--use-fake-ui-for-media-stream","--use-fake-device-for-media-stream","--autoplay-policy=no-user-gesture-required"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,permissions=["microphone","camera"])
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
    A.click('.tabbar [data-tab="together"]'); A.wait_for_timeout(200)
    A.click("#call-start"); A.wait_for_timeout(1200)
    print("A screen:",A.is_visible("#callscreen"),"|",A.inner_text("#cs-status"))
    A.screenshot(path=OUT+"call_A_out.png")
    print("B incoming:",B.is_visible("#cs-inc"),"|",B.inner_text("#cs-status"))
    B.screenshot(path=OUT+"call_B_in.png")
    B.click("#cb-accept"); A.wait_for_timeout(3500)
    print("A status:",A.inner_text("#cs-status"),"| B status:",B.inner_text("#cs-status"))
    A.click("#cb-mute"); print("mute on:",A.get_attribute("#cb-mute","class"))
    A.screenshot(path=OUT+"call_A_in.png")
    A.go_back(); A.wait_for_timeout(300); print("back -> pill:",A.is_visible("#callpill"),A.inner_text("#callpill"),"| screen hidden:",not A.is_visible("#callscreen"))
    A.screenshot(path=OUT+"call_A_pill.png")
    A.click("#callpill"); A.wait_for_timeout(200); print("restored:",A.is_visible("#callscreen"))
    B.click("#cs-chat"); B.wait_for_timeout(300); print("B chat during call:",B.is_visible("#s-chat"),"| pill:",B.is_visible("#callpill"))
    A.click("#cb-end"); B.wait_for_timeout(1200); print("ended both:",not A.is_visible("#callscreen"),not B.is_visible("#callscreen"),not B.is_visible("#callpill"))
    # video
    A.wait_for_timeout(1500); A.click("#call-video"); B.wait_for_timeout(1500); B.click("#cb-accept"); A.wait_for_timeout(4000)
    print("video class:",A.get_attribute("#callscreen","class"),"| flip visible:",A.is_visible("#cs-flip"))
    A.click("#cs-flip"); A.wait_for_timeout(1500); print("after flip has video:",A.evaluate("document.getElementById('local-video').srcObject.getVideoTracks().length"))
    A.screenshot(path=OUT+"call_A_video.png")
    A.click("#cs-min"); A.wait_for_timeout(300); print("video mini:",A.get_attribute("#vlayer","class"))
    A.screenshot(path=OUT+"call_A_videomin.png")
    A.click("#vlayer"); A.wait_for_timeout(200); print("restored video:",A.is_visible("#callscreen"))
    B.click("#cb-end"); A.wait_for_timeout(1200); print("ended:",not A.is_visible("#callscreen"))
    b.close()
print("ERRORS:",errs)
