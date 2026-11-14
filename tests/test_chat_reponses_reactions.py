import os, sys
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(HERE)+"/"; FIX=HERE+"/fixtures/"; MOCK=HERE+"/mock-firebase.js"
OUT=os.environ.get("ND_OUT","/tmp/nd-tests")+"/"; os.makedirs(OUT,exist_ok=True)
CHROME={"executable_path":os.environ["CHROME"]} if os.environ.get("CHROME") else {}
errs=[]
with sync_playwright() as p:
    b=p.chromium.launch(**CHROME,args=["--no-sandbox"])
    ctx=b.new_context(viewport={"width":390,"height":844},device_scale_factor=2,has_touch=False)
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
        pg.click('.tabbar [data-tab="chat"]'); pg.wait_for_timeout(200)
    A.fill("#ch-input","Tu as aimé ma lettre ?"); A.click("#ch-send"); B.wait_for_timeout(400)
    # B swipes right on A's message to reply
    bb=B.locator(".msg.theirs .bubble").first.bounding_box()
    B.mouse.move(bb["x"]+20,bb["y"]+bb["height"]/2); B.mouse.down(); 
    for i in range(1,9): B.mouse.move(bb["x"]+20+i*10,bb["y"]+bb["height"]/2)
    B.mouse.up(); B.wait_for_timeout(300)
    print("B reply bar:",B.is_visible("#ch-reply"),"|",B.inner_text("#ch-reply").replace("\n"," / "))
    B.fill("#ch-input","Oui beaucoup ")
    B.click("#ch-emo-btn"); B.wait_for_timeout(200); print("emoji panel:",B.is_visible("#ch-emo"),len(B.query_selector_all("#ch-emo button")))
    B.click("#ch-emo button >> nth=6"); B.click("#ch-emo button >> nth=48")
    print("input:",B.input_value("#ch-input"))
    B.click("#ch-send"); A.wait_for_timeout(400)
    print("A sees quote:",A.inner_text(".msg.theirs .quote").replace("\n"," / "),"| text:",A.inner_text(".msg.theirs .bubble").replace("\n"," / "))
    # A long-presses B's message -> react 😂
    bb=A.locator(".msg.theirs .bubble").first.bounding_box()
    A.mouse.move(bb["x"]+30,bb["y"]+bb["height"]-8); A.mouse.down(); A.wait_for_timeout(650); A.mouse.up(); A.wait_for_timeout(200)
    print("A menu:",A.is_visible(".rxbar"),"| actions:",A.inner_text(".mact").replace("\n"," | "))
    A.click(".rxbar button >> nth=1"); B.wait_for_timeout(400)
    print("B sees reaction on own msg:",B.inner_text(".msg.mine .rx"))
    # B double taps A's message for heart, then reacts via ➕ panel
    B.dblclick(".msg.theirs .bubble"); A.wait_for_timeout(400); print("A heart:",A.inner_text(".msg.mine .rx"))
    B.click('.tabbar [data-tab="home"]'); A.wait_for_timeout(100)
    bb=A.locator(".msg.theirs .bubble").first.bounding_box()
    A.mouse.move(bb["x"]+30,bb["y"]+bb["height"]-8); A.mouse.down(); A.wait_for_timeout(650); A.mouse.up(); A.wait_for_timeout(200)
    A.click(".rxbar button >> nth=6"); A.wait_for_timeout(150); A.click("#ch-emo button >> nth=67"); B.wait_for_timeout(500)
    print("B toast:",B.inner_text("#toast").replace("\n"," ") if B.query_selector("#toast") else "?")
    B.click('.tabbar [data-tab="chat"]'); B.wait_for_timeout(300)
    print("B rx now:",B.inner_text(".msg.mine .rx"))
    # click quote scrolls/flash
    A.click(".msg.theirs .quote"); A.wait_for_timeout(200); print("flash:",A.evaluate("!!document.querySelector('.msg.flash')"))
    A.locator(".msg.theirs .bubble").first.click(button="right"); A.wait_for_timeout(200); print("back closes menu:", end=" "); A.go_back(); A.wait_for_timeout(150); print(not A.is_visible(".rxbar"), A.is_visible("#s-chat"))
    B.screenshot(path=OUT+"chat2_B.png")
    A.locator(".msg.theirs .bubble").first.click(button="right"); A.wait_for_timeout(200); A.screenshot(path=OUT+"chat2_A_menu.png")
    b.close()
print("ERRORS:",errs)
