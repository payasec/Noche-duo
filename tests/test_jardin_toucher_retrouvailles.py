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
    for pg,n in ((A,"A"),(B,"B")): pg.on("pageerror",lambda e,n=n: errs.append(n+" "+str(e)))
    A.goto("http://localhost:8771/"); A.wait_for_timeout(400)
    A.click('.langbig[data-lang="fr"]'); A.click("#onb-next"); A.fill("#onb-me","Jean"); A.click("#onb-next"); A.click("#onb-later")
    A.click("#ol-create"); A.wait_for_timeout(300); code=A.inner_text("#ol-code-show")
    print("invite btn visible:",A.is_visible("#ol-invite"))
    url=A.evaluate("appURL() ") if False else None
    B.goto("http://localhost:8771/?join="+code+"&from=Jean"); B.wait_for_timeout(400)
    print("B url cleaned:",B.url)
    B.click('.langbig[data-lang="fr"]'); B.click("#onb-next"); B.fill("#onb-me","Nadia"); B.click("#onb-next"); B.click("#onb-later"); B.wait_for_timeout(200)
    print("B invite card:",B.is_visible("#invite-card"),"|",B.inner_text("#inv-title"))
    B.click("#inv-join"); B.wait_for_timeout(900)
    print("B linked, invite hidden:",not B.is_visible("#invite-card"),"| ol-linked:",B.is_visible("#ol-linked"))
    for pg in (A,B):
        if pg.is_visible("#moonx"): pg.click("#moonx")
    A.wait_for_timeout(400)
    print("garden A:",A.is_visible("#garden-card"),A.inner_text("#gd-stage"),"|",A.inner_text("#gd-next"))
    print("reunion A:",A.is_visible("#reu-card"),A.inner_text("#reu-title"))
    import datetime
    d=(datetime.date.today()+datetime.timedelta(days=12)).isoformat()
    A.fill("#reu-in",d); A.click("#reu-save"); A.wait_for_timeout(1300)
    print("A clock:",A.inner_text("#reu-clock").replace("\n"," "),"|",A.inner_text("#reu-line"))
    print("B reunion:",B.inner_text("#reu-title"),"|",B.inner_text("#reu-line"))
    A.click("#gd-water"); B.wait_for_timeout(600)
    print("B garden:",B.inner_text("#gd-me"),"|",B.inner_text("#gd-love"),"| next:",B.inner_text("#gd-next"))
    B.click("#gd-water"); A.wait_for_timeout(600)
    print("A after both:",A.inner_text("#gd-next"),"| btn:",A.inner_text("#gd-water"))
    A.screenshot(path=OUT+"w6_home_A.png",full_page=True)
    # simulate 30 days of watering to see the grown tree
    A.evaluate("""(function(){var u={};for(var i=1;i<=31;i++){var d=new Date();d.setDate(d.getDate()-i);u[dayKey(d)]={a:1,b:1};}
      return firebase.database().ref(olBase()+'/live/shared/garden').update(u);})()""") if False else None
    A.evaluate("""()=>{var ref=firebase.database().ref('couples/'+JSON.parse(localStorage.getItem('nd-profile')).couple.code+'/live/shared/garden');
      var arr=[];for(var i=1;i<=31;i++){var d=new Date();d.setDate(d.getDate()-i);arr.push(d.getFullYear()+'-'+(d.getMonth()+1)+'-'+d.getDate());}
      return Promise.all(arr.map(k=>ref.child(k).set({a:1,b:1})));}""")
    A.wait_for_timeout(1500)
    print("grown:",A.inner_text("#gd-stage"),"|",A.inner_text("#gd-note"),"| badge tree:",A.evaluate("JSON.parse(localStorage.getItem('nd-profile')).badges"))
    A.locator("#garden-card").screenshot(path=OUT+"w6_tree.png")
    # touch
    A.click('.tabbar [data-tab="together"]'); A.wait_for_timeout(200)
    A.hover("#touch-pad"); A.mouse.down(); A.wait_for_timeout(700)
    print("A touching:",A.inner_text("#tc-status"))
    B.wait_for_timeout(600); print("B toast/ask (on home):",B.inner_text("#toast") if B.query_selector("#toast") else "?")
    B.click('.tabbar [data-tab="together"]'); B.wait_for_timeout(300)
    print("B sees partner:",B.inner_text("#tc-status"))
    B.hover("#touch-pad"); B.mouse.down(); B.wait_for_timeout(11000)
    print("A both:",A.inner_text("#tc-status"),"|",A.inner_text("#tc-time"),"| classes:",A.get_attribute("#touch-pad","class"))
    print("touch badge B:", "touch" in B.evaluate("JSON.parse(localStorage.getItem('nd-profile')).badges"))
    B.screenshot(path=OUT+"w6_touch_B.png")
    A.mouse.up(); B.wait_for_timeout(1200); print("B after A lifts:",B.inner_text("#tc-status"))
    B.mouse.up()
    b.close()
print("ERRORS:",errs)
