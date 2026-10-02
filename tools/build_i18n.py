"""Erzeugt die englischen und tuerkischen Seiten (en/, tr/) aus den deutschen Originalen.

Nach jeder Textaenderung in index.html oder kiosk.html ausfuehren:
    python3 tools/build_i18n.py
Neue deutsche Texte brauchen einen Eintrag in den Listen INDEX/KIOSK, sonst bricht das Skript ab.
Der Ratgeber (was-ist-lahmacun.html) wird in allen drei Sprachen aus GUIDE erzeugt.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ENTITIES = {
    '&auml;': 'ä', '&ouml;': 'ö', '&uuml;': 'ü', '&Auml;': 'Ä', '&Ouml;': 'Ö', '&Uuml;': 'Ü',
    '&szlig;': 'ß', '&ndash;': '–', '&rarr;': '→', '&middot;': '·', '&euro;': '€',
    '&bdquo;': '„', '&ldquo;': '“', '&rsquo;': '’', '&sect;': '§',
}


def load(name):
    s = open(os.path.join(ROOT, name), encoding='utf-8').read()
    for k, v in ENTITIES.items():
        s = s.replace(k, v)
    return s


def item(de, en, tr):
    w = '<span class="menu-item-name">{}</span>'
    return (w.format(de), w.format(en), w.format(tr))


LANG_DE_INDEX = '''    <nav class="lang-switch" aria-label="Sprache wählen">
      <a href="./" hreflang="de" lang="de" aria-current="page">DE</a>
      <a href="en/" hreflang="en" lang="en">EN</a>
      <a href="tr/" hreflang="tr" lang="tr">TR</a>
    </nav>'''
LANG_DE_KIOSK = '''    <nav class="lang-switch" aria-label="Sprache wählen">
      <a href="kiosk.html" hreflang="de" lang="de" aria-current="page">DE</a>
      <a href="en/kiosk.html" hreflang="en" lang="en">EN</a>
      <a href="tr/kiosk.html" hreflang="tr" lang="tr">TR</a>
    </nav>'''


def lang_nav(lang, page):
    label = {'en': 'Choose language', 'tr': 'Dil seçin'}[lang]
    target = '' if page == 'index' else 'kiosk.html'
    links = []
    for code in ('de', 'en', 'tr'):
        if code == lang:
            href = target or './'
            links.append(f'      <a href="{href}" hreflang="{code}" lang="{code}" aria-current="page">{code.upper()}</a>')
        elif code == 'de':
            links.append(f'      <a href="../{target}" hreflang="de" lang="de">DE</a>')
        else:
            links.append(f'      <a href="../{code}/{target}" hreflang="{code}" lang="{code}">{code.upper()}</a>')
    return f'    <nav class="lang-switch" aria-label="{label}">\n' + '\n'.join(links) + '\n    </nav>'


# (german, english, turkish, expected_count)
COMMON = [
    ('aria-label="Menü öffnen"', 'aria-label="Open menu"', 'aria-label="Menüyü aç"'),
    ('<a href="#start">Start</a>', '<a href="#start">Home</a>', '<a href="#start">Ana Sayfa</a>'),
    ('<a href="#ueber-uns">Über uns</a>', '<a href="#ueber-uns">About us</a>', '<a href="#ueber-uns">Hakkımızda</a>'),
    ('<a href="#galerie">Galerie</a>', '<a href="#galerie">Gallery</a>', '<a href="#galerie">Galeri</a>'),
    ('<a href="#kontakt">Kontakt</a>', '<a href="#kontakt">Contact</a>', '<a href="#kontakt">İletişim</a>'),
    ('<span class="fact-label">Adresse</span>', '<span class="fact-label">Address</span>', '<span class="fact-label">Adres</span>'),
    ('<span class="fact-label">Telefon</span>', '<span class="fact-label">Phone</span>', '<span class="fact-label">Telefon</span>'),
    ('<span class="section-kicker">Über uns</span>', '<span class="section-kicker">About us</span>', '<span class="section-kicker">Hakkımızda</span>'),
    ('<span class="section-kicker">Galerie</span>', '<span class="section-kicker">Gallery</span>', '<span class="section-kicker">Galeri</span>'),
    ('<span class="section-kicker">Kontakt &amp; Standort</span>', '<span class="section-kicker">Contact &amp; location</span>', '<span class="section-kicker">İletişim &amp; konum</span>'),
    ('<dt>Adresse</dt>', '<dt>Address</dt>', '<dt>Adres</dt>'),
    ('<dt>Telefon</dt>', '<dt>Phone</dt>', '<dt>Telefon</dt>'),
    ('<dt>Öffnungszeiten</dt>', '<dt>Opening hours</dt>', '<dt>Çalışma saatleri</dt>'),
    ('<h3>Getränke</h3>', '<h3>Drinks</h3>', '<h3>İçecekler</h3>'),
    ('<p>Beim Laden der Karte wird eine Verbindung zu Google-Servern hergestellt und deine IP-Adresse an Google übertragen. Mehr dazu in der <a href="datenschutz.html">Datenschutzerklärung</a>.</p>',
     '<p>Loading the map connects to Google’s servers and sends your IP address to Google. More in our <a href="datenschutz.html">privacy policy</a> (in German).</p>',
     '<p>Haritayı yüklediğinizde Google sunucularına bağlanılır ve IP adresiniz Google’a iletilir. Ayrıntılar <a href="datenschutz.html">gizlilik politikamızda</a> (Almanca).</p>'),
    ('>Karte laden</button>', '>Load map</button>', '>Haritayı yükle</button>'),
    ('<a href="was-ist-lahmacun.html">Was ist Lahmacun?</a>', '<a href="was-ist-lahmacun.html">What is lahmacun?</a>', '<a href="was-ist-lahmacun.html">Lahmacun nedir?</a>'),
    ('<a href="impressum.html">Impressum</a>', '<a href="impressum.html">Legal notice (Impressum)</a>', '<a href="impressum.html">Künye (Impressum)</a>'),
    ('<a href="datenschutz.html">Datenschutz</a>', '<a href="datenschutz.html">Privacy</a>', '<a href="datenschutz.html">Gizlilik</a>'),
]

INDEX = [
    ('<title>Essah Urfa Lahmacun | Bester Lahmacun in Düsseldorf</title>',
     '<title>Essah Urfa Lahmacun | Best Lahmacun in Düsseldorf</title>',
     '<title>Essah Urfa Lahmacun | Düsseldorf’ta En İyi Lahmacun</title>'),
    ('content="Essah Urfa Lahmacun in Düsseldorf-Wersten: handgemachter Lahmacun nach Familienrezept, frisch aus dem Ofen. Dazu Döner, Pide und Pizza – Kölner Landstraße 263."',
     'content="Essah Urfa Lahmacun in Düsseldorf-Wersten: handmade lahmacun from a family recipe, fresh from the oven. Plus döner, pide and pizza – Kölner Landstraße 263."',
     'content="Essah Urfa Lahmacun, Düsseldorf-Wersten: aile tarifiyle elde açılan, fırından taze lahmacun. Döner, pide ve pizza da var – Kölner Landstraße 263."'),
    ('<link rel="canonical" href="https://essah-urfa.de/">',
     '<link rel="canonical" href="https://essah-urfa.de/en/">',
     '<link rel="canonical" href="https://essah-urfa.de/tr/">'),
    ('<meta property="og:title" content="Essah Urfa Lahmacun | Bester Lahmacun in Düsseldorf">',
     '<meta property="og:title" content="Essah Urfa Lahmacun | Best Lahmacun in Düsseldorf">',
     '<meta property="og:title" content="Essah Urfa Lahmacun | Düsseldorf’ta En İyi Lahmacun">'),
    ('content="Handgemachter Lahmacun nach Familienrezept, frisch aus dem Ofen – in Düsseldorf-Wersten, Kölner Landstraße 263."',
     'content="Handmade lahmacun from a family recipe, fresh from the oven – in Düsseldorf-Wersten, Kölner Landstraße 263."',
     'content="Aile tarifiyle elde açılan, fırından taze lahmacun – Düsseldorf-Wersten, Kölner Landstraße 263."'),
    ('<meta property="og:url" content="https://essah-urfa.de/">',
     '<meta property="og:url" content="https://essah-urfa.de/en/">',
     '<meta property="og:url" content="https://essah-urfa.de/tr/">'),
    ('aria-label="Essah Urfa auf Instagram"', 'aria-label="Essah Urfa on Instagram"', 'aria-label="Instagram’da Essah Urfa"'),
    ('<p class="top-banner-cross">Gehört zusammen mit der Trinkhalle by Fero – direkt nebenan <a href="kiosk.html">Zum Kiosk →</a></p>',
     '<p class="top-banner-cross">Sister shop of Trinkhalle by Fero – right next door <a href="kiosk.html">Visit the kiosk →</a></p>',
     '<p class="top-banner-cross">Trinkhalle by Fero ile kardeş dükkân – hemen yan tarafta <a href="kiosk.html">Büfeye git →</a></p>'),
    ('<a href="#speisekarte">Speisekarte</a>', '<a href="#speisekarte">Menu</a>', '<a href="#speisekarte">Menü</a>'),
    ('<a href="#bewertungen">Bewertungen</a>', '<a href="#bewertungen">Reviews</a>', '<a href="#bewertungen">Yorumlar</a>'),
    ('<a href="#faq">FAQ</a>', '<a href="#faq">FAQ</a>', '<a href="#faq">SSS</a>'),
    ('Original Urfa Art · frisch aus dem Ofen', 'Authentic Urfa style · fresh from the oven', 'Orijinal Urfa usulü · fırından taze'),
    ('<h1>Essah Urfa Lahmacun: Traditioneller handgemachter Lahmacun in Düsseldorf</h1>',
     '<h1>Essah Urfa Lahmacun: Traditional handmade lahmacun in Düsseldorf</h1>',
     '<h1>Essah Urfa Lahmacun: Düsseldorf’ta geleneksel, elde açılan lahmacun</h1>'),
    ('Dünner Teig, herzhafte Fülle, direkt aus Düsseldorf-Wersten. Seit Jahren an der Kölner Landstraße.',
     'Thin dough, savoury topping, straight from Düsseldorf-Wersten. On Kölner Landstraße for years.',
     'İnce hamur, bol harç, doğrudan Düsseldorf-Wersten’den. Yıllardır Kölner Landstraße’de.'),
    ('<h2>Lahmacun aus Düsseldorf-Wersten – handgemacht, wie es sein soll</h2>',
     '<h2>Lahmacun from Düsseldorf-Wersten – handmade, the way it should be</h2>',
     '<h2>Düsseldorf-Wersten’den lahmacun – olması gerektiği gibi, el yapımı</h2>'),
    ('<p>Mitten in Düsseldorf-Wersten, direkt an der Kölner Landstraße, backen wir bei Essah-Urfa jeden Tag frischen Lahmacun nach traditionellem Familienrezept. Der Teig wird täglich neu angesetzt und von Hand hauchdünn ausgerollt, die würzige Fülle mit frischen Kräutern abgeschmeckt – kein Fast Food von der Stange, sondern Handwerk, das man schmeckt.</p>',
     '<p>Right in Düsseldorf-Wersten, on Kölner Landstraße, we bake fresh lahmacun every day at Essah Urfa, following a traditional family recipe. The dough is made fresh daily and rolled out wafer-thin by hand, and the spicy topping is seasoned with fresh herbs – not fast food off the shelf, but craftsmanship you can taste.</p>',
     '<p>Düsseldorf-Wersten’in tam ortasında, Kölner Landstraße üzerinde, Essah Urfa’da her gün geleneksel aile tarifimizle taze lahmacun pişiriyoruz. Hamurumuz her gün yeniden yoğrulur ve elde incecik açılır, baharatlı harcı taze yeşilliklerle hazırlanır – hazır fast food değil, tadına varılan bir zanaat.</p>'),
    ('<p>Wer in Düsseldorf-Süd nach echtem Lahmacun sucht, findet bei uns mehr als nur die türkische Ofenspezialität: Unsere Speisekarte reicht von klassischem Döner über Pide bis zu Pizza im Lahmacun-Stil – für jeden Geschmack ist etwas dabei. Ob zum Mitnehmen oder gemütlich bei uns vor Ort: Wir legen Wert darauf, dass alles frisch zubereitet wird, nicht vorproduziert und aufgewärmt.</p>',
     '<p>If you’re looking for real lahmacun in the south of Düsseldorf, you’ll find more than just the Turkish oven classic here: our menu ranges from classic döner and pide to lahmacun-style pizza – there’s something for everyone. Take away or sit down with us: we make sure everything is freshly prepared, not pre-made and reheated.</p>',
     '<p>Düsseldorf’un güneyinde gerçek lahmacun arayanlar bizde fırın lezzetinden fazlasını bulur: Menümüz klasik dönerden pideye, lahmacun usulü pizzaya kadar uzanır – herkesin damak tadına uygun bir şey var. İster paket ister burada oturarak: Her şeyin önceden hazırlanıp ısıtılmadan, taze yapılmasına özen gösteriyoruz.</p>'),
    ('<p>Als kleiner, familiengeführter Imbiss in Wersten freuen wir uns über Stammgäste aus der Nachbarschaft genauso wie über alle, die aus anderen Teilen von Düsseldorf für ein gutes Stück Lahmacun zu uns kommen. Bei uns musst du dein Essen nicht im Stehen essen: Wir haben gemütliche Sitzplätze, an denen du in Ruhe essen kannst – dazu einen frischen Ayran oder ein kaltes Getränk. Ob spontan auf dem Heimweg durch Wersten oder als geplanter Besuch aus Düsseldorf-Süd: Schau vorbei, ruf an oder komm einfach rein.</p>',
     '<p>As a small, family-run takeaway in Wersten, we’re just as happy to welcome regulars from the neighbourhood as everyone who comes from other parts of Düsseldorf for a good lahmacun. You don’t have to eat standing up: we have comfortable seating where you can enjoy your food in peace – with a fresh ayran or a cold drink. Whether you drop in on your way home through Wersten or plan a visit from the south of Düsseldorf: come by, give us a call or just walk in.</p>',
     '<p>Wersten’de küçük bir aile işletmesi olarak hem mahalleden gelen müdavimlerimizi hem de güzel bir lahmacun için Düsseldorf’un diğer semtlerinden gelen herkesi memnuniyetle ağırlıyoruz. Bizde ayakta yemek zorunda değilsiniz: Rahat oturma yerlerimizde yemeğinizi huzurla yiyebilir, yanında taze bir ayran ya da soğuk bir içecek içebilirsiniz. İster Wersten’den eve dönerken uğrayın ister Düsseldorf’un güneyinden planlı gelin: Buyurun, arayın ya da doğrudan içeri girin.</p>'),
    ('alt="Theke bei Essah Urfa Lahmacun in Düsseldorf-Wersten mit frischen Zutaten und Dönerspieß"',
     'alt="Counter at Essah Urfa Lahmacun in Düsseldorf-Wersten with fresh ingredients and döner spit"',
     'alt="Düsseldorf-Wersten’deki Essah Urfa Lahmacun’da taze malzemeler ve döner şişiyle tezgâh"'),
    ('<h2 class="visually-hidden">Warum Essah Urfa?</h2>', '<h2 class="visually-hidden">Why Essah Urfa?</h2>', '<h2 class="visually-hidden">Neden Essah Urfa?</h2>'),
    ('<a href="was-ist-lahmacun.html">Ratgeber</a>', '<a href="was-ist-lahmacun.html">Guide</a>', '<a href="was-ist-lahmacun.html">Rehber</a>'),
    ('<h3>Täglich frisch</h3>', '<h3>Fresh every day</h3>', '<h3>Her gün taze</h3>'),
    ('<p>Teig und Fülle werden jeden Tag neu zubereitet – nichts liegt tagelang im Kühlhaus.</p>',
     '<p>Dough and topping are prepared fresh every day – nothing sits in the cold store for days.</p>',
     '<p>Hamur ve harç her gün yeniden hazırlanır – hiçbir şey günlerce soğuk depoda beklemez.</p>'),
    ('<h3>Familienrezept</h3>', '<h3>Family recipe</h3>', '<h3>Aile tarifi</h3>'),
    ('<p>Die Gewürzmischung für unsere Fülle geben wir seit Generationen weiter.</p>',
     '<p>The spice blend for our topping has been passed down for generations.</p>',
     '<p>Harcımızın baharat karışımı nesilden nesile aktarılıyor.</p>'),
    ('<h3>Große Auswahl</h3>', '<h3>Wide selection</h3>', '<h3>Geniş seçenek</h3>'),
    ('<p>Neben Lahmacun gibt es Döner, Pide, Pizza, Toast, Suppen und Getränke – für jeden Geschmack.</p>',
     '<p>Besides lahmacun we have döner, pide, pizza, toasties, soups and drinks – something for every taste.</p>',
     '<p>Lahmacunun yanı sıra döner, pide, pizza, tost, çorba ve içecekler – her damak tadına göre.</p>'),
    ('<h3>Faire Preise</h3>', '<h3>Fair prices</h3>', '<h3>Uygun fiyatlar</h3>'),
    ('<p>Ehrliches Essen zu einem Preis, der stimmt – egal ob zum Mitnehmen oder vor Ort.</p>',
     '<p>Honest food at the right price – whether you take it away or eat in.</p>',
     '<p>Dürüst yemek, doğru fiyat – ister paket ister yerinde.</p>'),
    ('<span class="section-kicker">Zubereitung</span>', '<span class="section-kicker">How we make it</span>', '<span class="section-kicker">Hazırlanışı</span>'),
    ('<h2>Von Teig bis Tisch</h2>', '<h2>From dough to table</h2>', '<h2>Hamurdan sofraya</h2>'),
    ('<h3>Teig ausrollen</h3>', '<h3>Rolling the dough</h3>', '<h3>Hamuru açmak</h3>'),
    ('<p>Der Lahmacun-Teig wird täglich frisch angesetzt und hauchdünn von Hand ausgerollt.</p>',
     '<p>The lahmacun dough is made fresh every day and rolled out wafer-thin by hand.</p>',
     '<p>Lahmacun hamuru her gün taze yoğrulur ve elde incecik açılır.</p>'),
    ('<h3>Fülle würzen</h3>', '<h3>Seasoning the topping</h3>', '<h3>Harcı hazırlamak</h3>'),
    ('<p>Die Hackfleischfülle wird nach Familienrezept mit frischen Kräutern und Gewürzen abgeschmeckt.</p>',
     '<p>The minced-meat topping is seasoned with fresh herbs and spices according to our family recipe.</p>',
     '<p>Kıymalı harç, aile tarifimize göre taze yeşillik ve baharatlarla tatlandırılır.</p>'),
    ('<h3>Im Ofen backen</h3>', '<h3>Baking in the oven</h3>', '<h3>Fırında pişirmek</h3>'),
    ('<p>Jeder Lahmacun kommt einzeln in den Ofen, bis der Rand knusprig und die Fülle saftig ist.</p>',
     '<p>Each lahmacun goes into the oven on its own until the edge is crisp and the topping juicy.</p>',
     '<p>Her lahmacun tek tek fırına girer; kenarı çıtır, harcı sulu olana kadar pişer.</p>'),
    ('<span class="section-kicker section-kicker--light">Speisekarte</span>', '<span class="section-kicker section-kicker--light">Menu</span>', '<span class="section-kicker section-kicker--light">Menü</span>'),
    ('<h2 class="menu-heading">Unsere Speisekarte für Düsseldorf-Süd</h2>',
     '<h2 class="menu-heading">Our menu for the south of Düsseldorf</h2>',
     '<h2 class="menu-heading">Düsseldorf-Süd için menümüz</h2>'),
    item('Lahmacun ohne alles', 'Plain lahmacun', 'Sade lahmacun'),
    item('Lahmacun mit Salat', 'Lahmacun with salad', 'Salatalı lahmacun'),
    item('Lahmacun vegetarisch', 'Vegetarian lahmacun', 'Vejetaryen lahmacun'),
    item('Peymacun mit Käse', 'Peymacun with cheese', 'Peynirli peymacun'),
    item('Lahmacun mit Dönerfleisch', 'Lahmacun with döner meat', 'Döner etli lahmacun'),
    item('Döner Tasche', 'Döner in pita bread', 'Ekmek arası döner'),
    item('Pom Döner', 'Pom döner (with fries)', 'Pom döner (patatesli)'),
    item('Döner Dürüm', 'Döner dürüm wrap', 'Dürüm döner'),
    item('Döner Teller klein', 'Döner plate, small', 'Döner tabağı, küçük'),
    item('Döner Teller groß', 'Döner plate, large', 'Döner tabağı, büyük'),
    item('Döner Portion klein', 'Döner portion, small', 'Porsiyon döner, küçük'),
    item('Döner Portion mittel', 'Döner portion, medium', 'Porsiyon döner, orta'),
    item('Döner Portion groß', 'Döner portion, large', 'Porsiyon döner, büyük'),
    item('Pide mit Käse', 'Pide with cheese', 'Kaşarlı pide'),
    item('Pide mit Sucuk', 'Pide with sucuk', 'Sucuklu pide'),
    item('Pide mit Spinat', 'Pide with spinach', 'Ispanaklı pide'),
    item('Pide mit Hackfleisch', 'Pide with minced meat', 'Kıymalı pide'),
    item('Pide mit Dönerfleisch', 'Pide with döner meat', 'Döner etli pide'),
    item('Pide mit Pastirma', 'Pide with pastirma', 'Pastırmalı pide'),
    item('Pide mit Gemischtem', 'Mixed pide', 'Karışık pide'),
    ('<h3>Vegetarisch</h3>', '<h3>Vegetarian</h3>', '<h3>Vejetaryen</h3>'),
    item('Falafel Tasche', 'Falafel in pita bread', 'Ekmek arası falafel'),
    item('Falafel Dürüm', 'Falafel dürüm wrap', 'Dürüm falafel'),
    item('Falafel Teller', 'Falafel plate', 'Falafel tabağı'),
    item('Salat Tasche', 'Salad in pita bread', 'Ekmek arası salata'),
    item('Pom Brot mit Salat', 'Bread with fries and salad', 'Patatesli salatalı ekmek'),
    item('Pom Falafel', 'Pom falafel (with fries)', 'Pom falafel (patatesli)'),
    item('Pizza Funghi', 'Pizza funghi', 'Mantarlı pizza'),
    item('Pizza Salami', 'Pizza salami', 'Salamlı pizza'),
    item('Pizza Thunfisch', 'Pizza tuna', 'Ton balıklı pizza'),
    item('Pizza Schinken', 'Pizza ham', 'Jambonlu pizza'),
    item('Pizza Vegetarisch', 'Vegetarian pizza', 'Vejetaryen pizza'),
    item('Pizza Döner', 'Pizza döner', 'Dönerli pizza'),
    item('Pizza Sucuk', 'Pizza sucuk', 'Sucuklu pizza'),
    ('<h3>Toast &amp; Suppe</h3>', '<h3>Toasties &amp; soup</h3>', '<h3>Tost &amp; çorba</h3>'),
    item('Toast mit Käse', 'Cheese toastie', 'Kaşarlı tost'),
    item('Toast mit Sucuk &amp; Käse', 'Sucuk &amp; cheese toastie', 'Sucuklu kaşarlı tost'),
    item('Linsensuppe', 'Lentil soup', 'Mercimek çorbası'),
    item('Tägliche Suppe', 'Soup of the day', 'Günün çorbası'),
    ('<h3>Pommes</h3>', '<h3>Fries</h3>', '<h3>Patates kızartması</h3>'),
    item('Pommes klein', 'Fries, small', 'Patates, küçük'),
    item('Pommes groß', 'Fries, large', 'Patates, büyük'),
    item('Wasser', 'Water', 'Su'),
    ('<h2>Einblicke aus dem Laden</h2>', '<h2>Inside the shop</h2>', '<h2>Dükkândan kareler</h2>'),
    ('alt="Frische Salate und Zutaten für Lahmacun und Döner an der Theke von Essah Urfa"',
     'alt="Fresh salads and ingredients for lahmacun and döner at the Essah Urfa counter"',
     'alt="Essah Urfa tezgâhında lahmacun ve döner için taze salatalar ve malzemeler"'),
    ('alt="Sitzbereich im Lahmacun-Imbiss Essah Urfa in Düsseldorf-Wersten"', 'alt="Seating area at the Essah Urfa lahmacun restaurant in Düsseldorf-Wersten"', 'alt="Düsseldorf-Wersten’deki Essah Urfa lahmacun salonunda oturma alanı"'),
    ('alt="Gemütliche Sitzecke mit Ledersitzen bei Essah Urfa Lahmacun"', 'alt="Cosy corner with leather seats at Essah Urfa Lahmacun"', 'alt="Essah Urfa Lahmacun’da deri koltuklu rahat köşe"'),
    ('alt="Sitzplätze am Fenster mit Blick auf die Kölner Landstraße"', 'alt="Window seats overlooking Kölner Landstraße"', 'alt="Kölner Landstraße’ye bakan pencere kenarı oturma yerleri"'),
    ('alt="Frisch gebackene Pide mit Spinat und Käse, dazu Gewürze und Limette"', 'alt="Freshly baked spinach and cheese pide with spices and lime"', 'alt="Baharat ve misket limonuyla fırından yeni çıkmış ıspanaklı peynirli pide"'),
    ('alt="Getränkekühlschrank mit alkoholfreien Cocktails und Limonaden bei Essah Urfa"',
     'alt="Drinks fridge with alcohol-free cocktails and lemonades at Essah Urfa"',
     'alt="Essah Urfa’da alkolsüz kokteyl ve limonatalarla içecek dolabı"'),
    ('<span class="section-kicker">Bewertungen</span>', '<span class="section-kicker">Reviews</span>', '<span class="section-kicker">Yorumlar</span>'),
    ('<h2>Was Gäste sagen</h2>', '<h2>What guests say</h2>', '<h2>Misafirlerimiz ne diyor</h2>'),
    ('<footer>Google-Rezension</footer>', '<footer>Google review · translated from German</footer>', '<footer>Google yorumu · Almancadan çevrilmiştir</footer>', 5),
    ('<p>Die 5-Sterne-Bewertungen sind absolut verdient! Der Dürüm Döner und der „normale“ Döner waren super im Geschmack – viel frisches Fleisch, frisches Gemüse und eine super leckere Sauce. Der Chef war sehr freundlich und hat uns sogar einen türkischen Tee aufs Haus angeboten. Man kann drinnen schön gemütlich sitzen. Für mich der leckerste Döner der letzten Zeit – das gilt für Hähnchen und Kalb. Auch die Preise sind gut.</p>',
     '<p>The 5-star reviews are absolutely deserved! The dürüm döner and the “regular” döner tasted great – lots of fresh meat, fresh vegetables and a really tasty sauce. The owner was very friendly and even offered us a Turkish tea on the house. You can sit inside nice and cosy. For me the tastiest döner in a long time – chicken and veal alike. The prices are good too.</p>',
     '<p>5 yıldızlı yorumlar sonuna kadar hak edilmiş! Dürüm döner de “normal” döner de çok lezzetliydi – bol taze et, taze sebze ve çok lezzetli bir sos. Dükkân sahibi çok güler yüzlüydü, hatta bize ikram olarak Türk çayı verdi. İçeride rahat rahat oturabiliyorsunuz. Benim için son zamanların en lezzetli döneri – hem tavuk hem dana. Fiyatlar da iyi.</p>'),
    ('<p>Alles wird frisch zubereitet und schmeckt super lecker. Die Pizzen sind allerdings nicht im italienischen, sondern im Lahmacun-Stil. Sehr aufmerksamer und netter Service – da komme ich gerne wieder!</p>',
     '<p>Everything is freshly made and tastes delicious. The pizzas aren’t Italian-style though, they’re lahmacun-style. Very attentive and friendly service – I’ll gladly come back!</p>',
     '<p>Her şey taze hazırlanıyor ve çok lezzetli. Ancak pizzalar İtalyan usulü değil, lahmacun usulü. Çok ilgili ve nazik hizmet – seve seve tekrar gelirim!</p>'),
    ('<p>OMG, besser geht’s nicht – das ist wie ein Traum, der beste Döner der ganzen Welt! War schon zweimal dort. Donnerstags kostet er 4,99&nbsp;€ statt 5,99&nbsp;€, und der Ayran ist für den einen Euro Aufpreis auf jeden Fall dabei. War mit Mutter und Bruder da, dann noch mal für meine kleine Nichte – und am Ende wollten auch Schwester und Cousine unbedingt eins.</p>',
     '<p>OMG, it doesn’t get better than this – it’s like a dream, the best döner in the whole world! I’ve been there twice already. On Thursdays it costs €4.99 instead of €5.99, and the ayran is definitely worth the one euro extra. I went with my mum and brother, then again for my little niece – and in the end my sister and cousin absolutely wanted one too.</p>',
     '<p>Aman Allahım, bundan iyisi olamaz – rüya gibi, dünyanın en iyi döneri! İki kez gittim. Perşembe günleri 5,99&nbsp;€ yerine 4,99&nbsp;€, bir euro farkla ayran da kesinlikle alınır. Annem ve kardeşimle gittim, sonra küçük yeğenim için bir kez daha – en sonunda ablam ve kuzenim de mutlaka istedi.</p>'),
    ('<p>Sehr guter Döner – Kalb oder Hähnchen, super Preis-Leistungs-Verhältnis, netter Chef. Absolute Empfehlung hier in Wersten.</p>',
     '<p>Very good döner – veal or chicken, great value for money, nice owner. Highly recommended here in Wersten.</p>',
     '<p>Çok iyi döner – dana ya da tavuk, fiyat-performans harika, dükkân sahibi çok nazik. Wersten’de kesinlikle tavsiye ederim.</p>'),
    ('<p>Im August 2025 war ich zum ersten Mal dort und hab mir einen Hähnchen- und einen Kalb-Döner geholt. Beide haben sehr gut geschmeckt. Das Brot könnte etwas länger getostet werden, aber sonst ein leckerer Döner.</p>',
     '<p>I went there for the first time in August 2025 and got a chicken döner and a veal döner. Both tasted very good. The bread could be toasted a little longer, but otherwise a tasty döner.</p>',
     '<p>Ağustos 2025’te ilk kez gittim, bir tavuk bir de dana döner aldım. İkisi de çok lezzetliydi. Ekmek biraz daha uzun kızartılabilirdi ama onun dışında lezzetli bir döner.</p>'),
    ('<span class="section-kicker">Fragen &amp; Antworten</span>', '<span class="section-kicker">Questions &amp; answers</span>', '<span class="section-kicker">Sorular &amp; cevaplar</span>'),
    ('<h2>Gut zu wissen</h2>', '<h2>Good to know</h2>', '<h2>Bilmekte fayda var</h2>'),
    ('<summary>Kann ich bei euch auch vor Ort essen?</summary>', '<summary>Can I eat in?</summary>', '<summary>Yerinde yemek yiyebilir miyim?</summary>'),
    ('<p>Ja, wir haben gemütliche Sitzplätze – auch direkt am Fenster mit Blick zur Straße.</p>',
     '<p>Yes, we have comfortable seating – including window seats looking out onto the street.</p>',
     '<p>Evet, rahat oturma yerlerimiz var – sokağa bakan pencere kenarında da.</p>'),
    ('<summary>Habt ihr auch vegetarische Gerichte?</summary>', '<summary>Do you have vegetarian dishes?</summary>', '<summary>Vejetaryen yemekleriniz var mı?</summary>'),
    ('<p>Klar. Zum Beispiel Falafel Tasche, Falafel Dürüm, Falafel Teller oder Lahmacun vegetarisch.</p>',
     '<p>Of course. For example falafel in pita bread, falafel dürüm, a falafel plate or vegetarian lahmacun.</p>',
     '<p>Tabii. Örneğin ekmek arası falafel, dürüm falafel, falafel tabağı ya da vejetaryen lahmacun.</p>'),
    ('<summary>Gibt es bei euch nur Lahmacun?</summary>', '<summary>Do you only serve lahmacun?</summary>', '<summary>Sadece lahmacun mu var?</summary>'),
    ('<p>Nein. Neben Lahmacun findest du bei uns Döner, Pide, Pizza, Toast, Suppen, Pommes und Getränke. Was Lahmacun von Döner und Pide unterscheidet, erklären wir in unserem <a href="was-ist-lahmacun.html">Lahmacun-Ratgeber</a>.</p>',
     '<p>No. Besides lahmacun you’ll find döner, pide, pizza, toasties, soups, fries and drinks. What makes lahmacun different from döner and pide is explained in our <a href="was-ist-lahmacun.html">lahmacun guide</a>.</p>',
     '<p>Hayır. Lahmacunun yanı sıra döner, pide, pizza, tost, çorba, patates kızartması ve içecekler de var. Lahmacunu döner ve pideden ayıran şeyi <a href="was-ist-lahmacun.html">lahmacun rehberimizde</a> anlatıyoruz.</p>'),
    ('<summary>Wie erreiche ich euch am schnellsten?</summary>', '<summary>What’s the quickest way to reach you?</summary>', '<summary>Size en hızlı nasıl ulaşırım?</summary>'),
    ('<p>Ruf uns einfach an unter <a href="tel:+4921197170255">0211 97170255</a> oder komm direkt vorbei an der Kölner Landstraße 263 in Düsseldorf.</p>',
     '<p>Just call us on <a href="tel:+4921197170255">0211 97170255</a> or drop by at Kölner Landstraße 263 in Düsseldorf.</p>',
     '<p>Bizi <a href="tel:+4921197170255">0211 97170255</a> numarasından arayın ya da doğrudan Düsseldorf’taki Kölner Landstraße 263 adresine uğrayın.</p>'),
    ('<h2>Besuch uns</h2>', '<h2>Visit us</h2>', '<h2>Bizi ziyaret edin</h2>'),
    ('''              Mo – Do: 11:00 – 01:00 Uhr<br>
              Fr – So: 11:00 – 02:00 Uhr''',
     '''              Mon – Thu: 11:00 – 01:00<br>
              Fri – Sun: 11:00 – 02:00''',
     '''              Pzt – Per: 11:00 – 01:00<br>
              Cum – Paz: 11:00 – 02:00'''),
    ('data-map-title="Standort Essah-Urfa auf der Karte"', 'data-map-title="Essah Urfa location on the map"', 'data-map-title="Essah Urfa’nın haritadaki konumu"'),
]

KIOSK = [
    ('<title>Trinkhalle by Fero | Kiosk &amp; Lotto in Düsseldorf-Wersten</title>',
     '<title>Trinkhalle by Fero | Kiosk &amp; Lottery in Düsseldorf-Wersten</title>',
     '<title>Trinkhalle by Fero | Düsseldorf-Wersten’de Büfe &amp; Loto</title>'),
    ('content="Trinkhalle by Fero (Lotto-Annahmestelle Zikos) in Düsseldorf-Wersten: Lotto, Zeitschriften, Snacks und Getränke – direkt neben Essah Urfa Lahmacun."',
     'content="Trinkhalle by Fero (Lotto-Annahmestelle Zikos) in Düsseldorf-Wersten: lottery, magazines, snacks and drinks – right next to Essah Urfa Lahmacun."',
     'content="Trinkhalle by Fero (Lotto-Annahmestelle Zikos), Düsseldorf-Wersten: loto, dergi, atıştırmalık ve içecek – Essah Urfa Lahmacun’un hemen yanında."'),
    ('<link rel="canonical" href="https://essah-urfa.de/kiosk.html">',
     '<link rel="canonical" href="https://essah-urfa.de/en/kiosk.html">',
     '<link rel="canonical" href="https://essah-urfa.de/tr/kiosk.html">'),
    ('<meta property="og:title" content="Trinkhalle by Fero – Lotto-Annahmestelle Zikos, Düsseldorf">',
     '<meta property="og:title" content="Trinkhalle by Fero – Lotto-Annahmestelle Zikos, Düsseldorf">',
     '<meta property="og:title" content="Trinkhalle by Fero – Lotto-Annahmestelle Zikos, Düsseldorf">'),
    ('content="Lotto, Zeitschriften, Snacks und Getränke direkt neben Essah-Urfa Lahmacun. Kölner Landstraße 263, Düsseldorf."',
     'content="Lottery, magazines, snacks and drinks right next to Essah Urfa Lahmacun. Kölner Landstraße 263, Düsseldorf."',
     'content="Essah Urfa Lahmacun’un hemen yanında loto, dergi, atıştırmalık ve içecek. Kölner Landstraße 263, Düsseldorf."'),
    ('<meta property="og:url" content="https://essah-urfa.de/kiosk.html">',
     '<meta property="og:url" content="https://essah-urfa.de/en/kiosk.html">',
     '<meta property="og:url" content="https://essah-urfa.de/tr/kiosk.html">'),
    ('<p class="top-banner-cross">Gehört zusammen mit Essah Urfa Lahmacun – direkt nebenan <a href="./">Zum Lahmacunladen →</a></p>',
     '<p class="top-banner-cross">Sister shop of Essah Urfa Lahmacun – right next door <a href="./">Visit the lahmacun shop →</a></p>',
     '<p class="top-banner-cross">Essah Urfa Lahmacun ile kardeş dükkân – hemen yan tarafta <a href="./">Lahmacun salonuna git →</a></p>'),
    ('<a href="#sortiment">Sortiment</a>', '<a href="#sortiment">Products</a>', '<a href="#sortiment">Ürünler</a>'),
    ('<p class="hero-eyebrow">Direkt neben Essah-Urfa Lahmacun</p>', '<p class="hero-eyebrow">Right next to Essah Urfa Lahmacun</p>', '<p class="hero-eyebrow">Essah Urfa Lahmacun’un hemen yanında</p>'),
    ('<p class="hero-text">Lotto, Zeitschriften, Snacks und Getränke für zwischendurch – gleich neben dem Lahmacunladen.</p>',
     '<p class="hero-text">Lottery, magazines, snacks and drinks for in between – right next to the lahmacun shop.</p>',
     '<p class="hero-text">Loto, dergi, atıştırmalık ve içecekler – lahmacun salonunun hemen yanında.</p>'),
    ('<h2>Alles für unterwegs</h2>', '<h2>Everything for on the go</h2>', '<h2>Yolda ne lazımsa</h2>'),
    ('<p>Direkt neben Essah-Urfa Lahmacun findest du die Trinkhalle by Fero, gleichzeitig Lotto-Annahmestelle Zikos – für alles, was noch auf den Tisch oder in die Tasche soll: Lotto, Zeitschriften, Getränke, Snacks und mehr.</p>',
     '<p>Right next to Essah Urfa Lahmacun you’ll find Trinkhalle by Fero, which is also the Zikos lottery outlet – for everything you still need for the table or your bag: lottery, magazines, drinks, snacks and more.</p>',
     '<p>Essah Urfa Lahmacun’un hemen yanında Trinkhalle by Fero’yu bulursunuz; burası aynı zamanda Zikos loto bayisidir – sofraya ya da çantaya ne lazımsa: loto, dergi, içecek, atıştırmalık ve daha fazlası.</p>'),
    ('<p>Ob vor oder nach dem Lahmacun – schau einfach kurz rein.</p>', '<p>Before or after your lahmacun – just pop in.</p>', '<p>Lahmacundan önce ya da sonra – bir uğrayın.</p>'),
    ('alt="Ladenfront der Trinkhalle by Fero mit WestLotto-Schild an der Kölner Landstraße 263 in Düsseldorf-Wersten"',
     'alt="Trinkhalle by Fero shop front with WestLotto sign at Kölner Landstraße 263 in Düsseldorf-Wersten"',
     'alt="Düsseldorf-Wersten, Kölner Landstraße 263’te WestLotto tabelalı Trinkhalle by Fero cephesi"'),
    ('<span class="section-kicker section-kicker--light">Sortiment</span>', '<span class="section-kicker section-kicker--light">Products</span>', '<span class="section-kicker section-kicker--light">Ürünler</span>'),
    ('<h2 class="menu-heading">Was es bei uns gibt</h2>', '<h2 class="menu-heading">What we stock</h2>', '<h2 class="menu-heading">Neler var</h2>'),
    ('<h3>Zeitschriften &amp; Zeitungen</h3>', '<h3>Magazines &amp; newspapers</h3>', '<h3>Dergi &amp; gazete</h3>'),
    item('Tageszeitungen', 'Daily newspapers', 'Günlük gazeteler'),
    item('Zeitschriften &amp; Magazine', 'Magazines', 'Dergiler'),
    ('<h3>Snacks &amp; Süßes</h3>', '<h3>Snacks &amp; sweets</h3>', '<h3>Atıştırmalık &amp; tatlı</h3>'),
    item('Chips &amp; Knäbberzeug', 'Crisps &amp; nibbles', 'Cips &amp; çerez'),
    item('Süßigkeiten &amp; Riegel', 'Sweets &amp; bars', 'Şekerleme &amp; bar'),
    item('Softdrinks &amp; Wasser', 'Soft drinks &amp; water', 'Meşrubat &amp; su'),
    item('Energy Drinks', 'Energy drinks', 'Enerji içecekleri'),
    ('<h3>Sonstiges</h3>', '<h3>Other</h3>', '<h3>Diğer</h3>'),
    item('Tabakwaren', 'Tobacco', 'Tütün ürünleri'),
    item('Lotto &amp; Rubbellose', 'Lottery &amp; scratch cards', 'Loto &amp; kazı kazan'),
    ('<h2>Einblicke in den Kiosk</h2>', '<h2>Inside the kiosk</h2>', '<h2>Büfeden kareler</h2>'),
    ('alt="Zigaretten- und Tabakregal in der Trinkhalle by Fero"', 'alt="Cigarette and tobacco shelf at Trinkhalle by Fero"', 'alt="Trinkhalle by Fero’da sigara ve tütün rafı"'),
    ('alt="Süßigkeiten-Ecke im Kiosk Trinkhalle by Fero"', 'alt="Sweets corner at the Trinkhalle by Fero kiosk"', 'alt="Trinkhalle by Fero büfesinde şekerleme köşesi"'),
    ('alt="Kühlschrank mit Bier und Spirituosen im Kiosk in Düsseldorf-Wersten"', 'alt="Fridge with beer and spirits at the kiosk in Düsseldorf-Wersten"', 'alt="Düsseldorf-Wersten’deki büfede bira ve alkollü içecek dolabı"'),
    ('alt="Regal mit Chips, Schokolade und Eis in der Trinkhalle by Fero"', 'alt="Shelf with crisps, chocolate and ice cream at Trinkhalle by Fero"', 'alt="Trinkhalle by Fero’da cips, çikolata ve dondurma rafı"'),
    ('alt="Eingang der Trinkhalle by Fero mit Leuchtreklame, direkt neben Essah Urfa Lahmacun"', 'alt="Trinkhalle by Fero entrance with illuminated sign, right next to Essah Urfa Lahmacun"', 'alt="Trinkhalle by Fero’nun ışıklı tabelalı girişi, Essah Urfa Lahmacun’un hemen yanında"'),
    ('alt="WestLotto-Terminals der Lotto-Annahmestelle Zikos"', 'alt="WestLotto terminals at the Zikos lottery outlet"', 'alt="Zikos loto bayisindeki WestLotto terminalleri"'),
    ('<h2>Direkt nebenan</h2>', '<h2>Right next door</h2>', '<h2>Hemen yan tarafta</h2>'),
    ('<small>(direkt neben Essah-Urfa Lahmacun)</small>', '<small>(right next to Essah Urfa Lahmacun)</small>', '<small>(Essah Urfa Lahmacun’un hemen yanında)</small>'),
    ('''              Mo – Do: 07:30 – 13:00 &amp; 14:30 – 18:30 Uhr<br>
              Fr: 07:30 – 18:30 Uhr<br>
              Sa: 07:30 – 13:00 Uhr<br>
              So: geschlossen''',
     '''              Mon – Thu: 07:30 – 13:00 &amp; 14:30 – 18:30<br>
              Fri: 07:30 – 18:30<br>
              Sat: 07:30 – 13:00<br>
              Sun: closed''',
     '''              Pzt – Per: 07:30 – 13:00 &amp; 14:30 – 18:30<br>
              Cum: 07:30 – 18:30<br>
              Cmt: 07:30 – 13:00<br>
              Paz: kapalı'''),
    ('data-map-title="Standort Trinkhalle by Fero auf der Karte"', 'data-map-title="Trinkhalle by Fero location on the map"', 'data-map-title="Trinkhalle by Fero’nun haritadaki konumu"'),
    ('<a href="./">Essah-Urfa Lahmacun →</a>', '<a href="./">Essah Urfa Lahmacun →</a>', '<a href="./">Essah Urfa Lahmacun →</a>'),
]

PATHS = [
    ('href="css/style.css"', 'href="../css/style.css"'),
    ("url('images/", "url('../images/"),
    ('src="images/', 'src="../images/'),
    ('src="js/script.js"', 'src="../js/script.js"'),
    ('href="impressum.html"', 'href="../impressum.html"'),
    ('href="datenschutz.html"', 'href="../datenschutz.html"'),
]


def build(src, page, pairs, lang):
    s = load(src)
    col = {'en': 1, 'tr': 2}[lang]
    s = s.replace('<html lang="de">', f'<html lang="{lang}">')
    s = s.replace('<meta property="og:locale" content="de_DE">',
                  '<meta property="og:locale" content="{}">'.format({'en': 'en_GB', 'tr': 'tr_TR'}[lang]))
    lang_de = LANG_DE_INDEX if page == 'index' else LANG_DE_KIOSK
    assert s.count(lang_de) == 1, ('lang nav', src)
    s = s.replace(lang_de, lang_nav(lang, page))
    for p in COMMON + pairs:
        de, new = p[0], p[col]
        expected = p[3] if len(p) > 3 else None
        n = s.count(de)
        if p in COMMON:
            if n == 0:
                continue
        elif expected is not None:
            assert n == expected, (lang, src, de[:70], n)
        else:
            assert n == 1, (lang, src, de[:70], n)
        s = s.replace(de, new)
    for old, new in PATHS:
        s = s.replace(old, new)
    out_dir = os.path.join(ROOT, lang)
    os.makedirs(out_dir, exist_ok=True)
    open(os.path.join(out_dir, src), 'w', encoding='utf-8').write(s)
    return s


GERMAN_HINTS = re.compile(r'\b(und|oder|nicht|wird|Uhr|bei uns|direkt|Laden|frisch|Speisekarte|Sitzpl|geschlossen|Zeitschriften|Getränke|Über|über)\b')

for lang in ('en', 'tr'):
    for src, page, pairs in (('index.html', 'index', INDEX), ('kiosk.html', 'kiosk', KIOSK)):
        out = build(src, page, pairs, lang)
        body = out[out.index('<body>'):]
        text = re.sub(r'<script.*?</script>', ' ', body, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', text)
        hits = sorted(set(m.group(0) for m in GERMAN_HINTS.finditer(text)))
        print(lang, src, 'possible German leftovers:', hits)


# ---------------------------------------------------------------- guide page
import json, html as htmllib
DIMS = json.load(open(os.path.join(ROOT, 'tools', 'image-dims.json')))
IG_SVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.4"/><circle cx="17.6" cy="6.4" r="1.2" class="dot"/></svg>'

GUIDE = {
 'de': dict(
  title='Was ist Lahmacun? Unterschied zu Döner &amp; Pide | Essah Urfa',
  desc='Was ist Lahmacun und was unterscheidet ihn von Döner und Pide? Herkunft, Zubereitung und Tipps – erklärt von Essah Urfa Lahmacun in Düsseldorf-Wersten.',
  og_title='Was ist Lahmacun? Unterschied zu Döner und Pide',
  og_desc='Herkunft, Zubereitung und der Unterschied zu Döner und Pide – einfach erklärt.',
  locale='de_DE', ig_label='Essah Urfa auf Instagram', lang_label='Sprache wählen',
  cross='Gehört zusammen mit der Trinkhalle by Fero – direkt nebenan <a href="kiosk.html">Zum Kiosk →</a>',
  nav=('Zur Startseite','Speisekarte','Kontakt'), kicker='Ratgeber',
  h1='Was ist Lahmacun? Der Unterschied zu Döner und Pide',
  alt1='Theke von Essah Urfa Lahmacun in Düsseldorf mit Dönerspieß und frischen Zutaten',
  intro="Wer nicht täglich in der türkischen Küche unterwegs ist, wirft Lahmacun, Döner und Pide schnell in einen Topf – verständlich, denn alle drei gibt’s oft im selben Laden. Dabei sind es drei ganz unterschiedliche Gerichte, mit eigener Zubereitung und eigener Herkunft.",
  h2a='Lahmacun: Herkunft und Zubereitung',
  pa1='Lahmacun ist ein hauchdünner, knuspriger Fladen aus ungesäuertem Teig, der mit einer würzigen Mischung aus fein gehacktem Fleisch, Tomaten, Paprika, Zwiebeln und Kräutern bestrichen und dann bei sehr hoher Hitze kurz gebacken wird. Der Name kommt aus dem Arabischen und bedeutet sinngemäß „Fleisch mit Teig“. Besonders bekannt ist die Variante aus der Region um Urfa und Gaziantep im Südosten der Türkei – daher auch die Bezeichnung „Urfa Art“, die auf würzige, oft leicht schärfere Füllungen anspielt.',
  pa2='Gegessen wird Lahmacun traditionell zusammengerollt oder gefaltet, meist belegt mit frischem Salat, Petersilie, Zwiebeln und einem Spritzer Zitrone. Er wird oft als „türkische Pizza“ bezeichnet – der Vergleich hinkt allerdings: Es gibt klassischerweise keinen Käse, der Teig ist viel dünner und knuspriger, und er wird deutlich heißer und kürzer gebacken.',
  h2b='Was ist der Unterschied zu Döner?',
  pb='Döner ist auf einem senkrechten Spieß gegartes, geschichtetes Fleisch (Hähnchen oder Kalb/Rind), das dünn abgeschnitten und in Fladenbrot, Tasche oder Dürüm-Wrap mit Salat und Sauce serviert wird. Bei Lahmacun dagegen ist das Fleisch von Anfang an Teil des Teigbelags und wird mitgebacken, nicht separat gegart und nachträglich aufgelegt. Kurz gesagt: Döner ist Spießfleisch im Brot, Lahmacun ist ein gebackener Fladen mit Fleischbelag.',
  h2c='Was ist der Unterschied zu Pide?',
  alt2='Pide mit Spinat und Käse – dicker als Lahmacun und mit hochgezogenem Rand',
  pc='Pide ist ein deutlich dickerer, länglicher Hefeteig-Fladen mit hochgezogenem Rand, oft „Bootsform“ genannt. Er wird meist mit Käse, Ei, Hackfleisch, Sucuk oder Gemüse gefüllt bzw. belegt und im Ofen gebacken – das kommt dem Bild einer „Pizza“ schon näher als Lahmacun. Der Teig ist luftiger und weicher, der Belag meist großzügiger. Lahmacun bleibt dagegen dünn, knusprig und eher schlicht belegt.',
  h2d='Lahmacun, Döner und Pide in Düsseldorf-Wersten',
  pd='Bei Essah Urfa Lahmacun an der Kölner Landstraße 263 in Düsseldorf-Wersten bekommst du alle drei – frisch zubereitet, mit hausgemachter Füllung und täglich frischem Teig. Wer sich nicht entscheiden kann: Genau dafür gibt es unsere <a href="./#speisekarte">Speisekarte</a>. Und gleich nebenan in der <a href="kiosk.html">Trinkhalle by Fero</a> gibt’s Getränke, Snacks und Lotto.',
  home='Startseite', foot_home='Zur Startseite', imp='Impressum', priv='Datenschutz',
 ),
 'en': dict(
  title='What is Lahmacun? Lahmacun vs. Döner &amp; Pide | Essah Urfa',
  desc='What is lahmacun and how is it different from döner and pide? Origin, preparation and tips – explained by Essah Urfa Lahmacun in Düsseldorf-Wersten.',
  og_title='What is lahmacun? The difference from döner and pide',
  og_desc='Origin, preparation and the difference from döner and pide – simply explained.',
  locale='en_GB', ig_label='Essah Urfa on Instagram', lang_label='Choose language',
  cross='Sister shop of Trinkhalle by Fero – right next door <a href="kiosk.html">Visit the kiosk →</a>',
  nav=('Home','Menu','Contact'), kicker='Guide',
  h1='What is lahmacun? The difference from döner and pide',
  alt1='Counter at Essah Urfa Lahmacun in Düsseldorf with döner spit and fresh ingredients',
  intro='If you don’t eat Turkish food every day, it’s easy to lump lahmacun, döner and pide together – understandable, since you often find all three in the same shop. Yet they are three quite different dishes, each with its own preparation and origin.',
  h2a='Lahmacun: origin and preparation',
  pa1='Lahmacun is a wafer-thin, crispy flatbread made from unleavened dough, spread with a spicy mix of finely minced meat, tomatoes, peppers, onions and herbs, then baked briefly at very high heat. The name comes from Arabic and roughly means “meat with dough”. The version from the region around Urfa and Gaziantep in south-eastern Turkey is especially well known – hence the term “Urfa style”, which refers to spicy, often slightly hotter toppings.',
  pa2='Lahmacun is traditionally eaten rolled up or folded, usually topped with fresh salad, parsley, onions and a squeeze of lemon. It is often called “Turkish pizza” – but the comparison falls short: there is traditionally no cheese, the dough is much thinner and crispier, and it is baked far hotter and shorter.',
  h2b='What is the difference from döner?',
  pb='Döner is layered meat (chicken or veal/beef) cooked on a vertical spit, sliced thinly and served in flatbread, pita or a dürüm wrap with salad and sauce. With lahmacun, on the other hand, the meat is part of the topping from the start and is baked together with the dough, not cooked separately and added afterwards. In short: döner is spit-roasted meat in bread, lahmacun is a baked flatbread with a meat topping.',
  h2c='What is the difference from pide?',
  alt2='Spinach and cheese pide – thicker than lahmacun and with a raised edge',
  pc='Pide is a much thicker, elongated yeast-dough flatbread with a raised edge, often described as “boat-shaped”. It is usually filled or topped with cheese, egg, minced meat, sucuk or vegetables and baked in the oven – which comes closer to the idea of a “pizza” than lahmacun. The dough is airier and softer, the topping usually more generous. Lahmacun, by contrast, stays thin, crispy and simply topped.',
  h2d='Lahmacun, döner and pide in Düsseldorf-Wersten',
  pd='At Essah Urfa Lahmacun, Kölner Landstraße 263 in Düsseldorf-Wersten, you can get all three – freshly prepared, with a homemade topping and dough made fresh every day. Can’t decide? That’s exactly what our <a href="./#speisekarte">menu</a> is for. And right next door at <a href="kiosk.html">Trinkhalle by Fero</a> you’ll find drinks, snacks and lottery tickets.',
  home='Home', foot_home='Home', imp='Legal notice (Impressum)', priv='Privacy',
 ),
 'tr': dict(
  title='Lahmacun Nedir? Döner ve Pideden Farkı | Essah Urfa',
  desc='Lahmacun nedir, döner ve pideden farkı ne? Kökeni, hazırlanışı ve ipuçları – Düsseldorf-Wersten’deki Essah Urfa Lahmacun anlatıyor.',
  og_title='Lahmacun nedir? Döner ve pideden farkı',
  og_desc='Kökeni, hazırlanışı ve döner ile pideden farkı – kısaca anlatıldı.',
  locale='tr_TR', ig_label='Instagram’da Essah Urfa', lang_label='Dil seçin',
  cross='Trinkhalle by Fero ile kardeş dükkân – hemen yan tarafta <a href="kiosk.html">Büfeye git →</a>',
  nav=('Ana Sayfa','Menü','İletişim'), kicker='Rehber',
  h1='Lahmacun nedir? Döner ve pideden farkı',
  alt1='Düsseldorf’taki Essah Urfa Lahmacun’da döner şişi ve taze malzemelerle tezgâh',
  intro='Türk mutfağını her gün yemeyenler lahmacun, döner ve pideyi kolayca birbirine karıştırır – anlaşılır bir durum, çünkü üçü de çoğu zaman aynı dükkânda bulunur. Oysa bunlar her biri kendi hazırlanışı ve kökeni olan üç ayrı yemektir.',
  h2a='Lahmacun: kökeni ve hazırlanışı',
  pa1='Lahmacun, mayasız hamurdan yapılan incecik ve çıtır bir yufkadır; üzerine ince kıyılmış et, domates, biber, soğan ve yeşilliklerden oluşan baharatlı bir harç sürülür ve çok yüksek ısıda kısa süre pişirilir. Adı Arapçadan gelir ve kabaca “hamurlu et” anlamına gelir. Özellikle Türkiye’nin güneydoğusunda Urfa ve Antep yöresinin lahmacunu meşhurdur – baharatlı, genellikle biraz daha acı harca işaret eden “Urfa usulü” ifadesi de buradan gelir.',
  pa2='Lahmacun geleneksel olarak dürülerek ya da katlanarak, genellikle taze salata, maydanoz, soğan ve biraz limonla yenir. Sık sık “Türk pizzası” diye anılır – ama bu benzetme eksik kalır: Geleneksel olarak peynir yoktur, hamuru çok daha ince ve çıtırdır, ayrıca çok daha yüksek ısıda ve daha kısa sürede pişer.',
  h2b='Dönerden farkı nedir?',
  pb='Döner, dik bir şişte pişirilen katmanlı ettir (tavuk ya da dana); ince ince kesilir ve pide ekmeği, ekmek arası ya da dürüm olarak salata ve sosla servis edilir. Lahmacunda ise et baştan harcın bir parçasıdır ve hamurla birlikte pişer; ayrı pişirilip sonradan eklenmez. Kısacası: Döner ekmek arasında şiş eti, lahmacun ise üzeri kıymalı fırınlanmış bir yufkadır.',
  h2c='Pideden farkı nedir?',
  alt2='Ispanaklı peynirli pide – lahmacundan daha kalın ve kenarı kalkık',
  pc='Pide, kenarları kalkık, çok daha kalın ve uzun bir mayalı hamurdur; çoğu zaman “kayık şeklinde” diye tarif edilir. Genellikle peynir, yumurta, kıyma, sucuk ya da sebzeyle doldurulup fırında pişirilir – bu da “pizza” fikrine lahmacundan daha yakındır. Hamuru daha kabarık ve yumuşak, iç malzemesi genellikle daha boldur. Lahmacun ise ince, çıtır ve sade kalır.',
  h2d='Düsseldorf-Wersten’de lahmacun, döner ve pide',
  pd='Düsseldorf-Wersten’de, Kölner Landstraße 263’teki Essah Urfa Lahmacun’da üçünü de bulabilirsiniz – taze hazırlanmış, ev yapımı harç ve her gün taze yoğrulan hamurla. Karar veremiyor musunuz? <a href="./#speisekarte">Menümüz</a> tam da bunun için var. Hemen yandaki <a href="kiosk.html">Trinkhalle by Fero</a>’da da içecek, atıştırmalık ve loto bulabilirsiniz.',
  home='Ana Sayfa', foot_home='Ana Sayfa', imp='Künye (Impressum)', priv='Gizlilik',
 ),
}


def guide_page(lang):
    g = GUIDE[lang]
    pre = '' if lang == 'de' else '../'
    url = 'https://essah-urfa.de/' + ('' if lang == 'de' else lang + '/') + 'was-ist-lahmacun.html'
    home_url = 'https://essah-urfa.de/' + ('' if lang == 'de' else lang + '/')
    def im(p):
        w, h = DIMS[p]
        return f'src="{pre}{p}" width="{w}" height="{h}"'
    langs = []
    for code in ('de', 'en', 'tr'):
        if code == lang:
            href = 'was-ist-lahmacun.html'; cur = ' aria-current="page"'
        else:
            href = (pre if code == 'de' else pre + code + '/') + 'was-ist-lahmacun.html'
            if lang == 'de':
                href = code + '/was-ist-lahmacun.html'
            cur = ''
        langs.append(f'      <a href="{href}" hreflang="{code}" lang="{code}"{cur}>{code.upper()}</a>')
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {'@type': 'Article', 'headline': htmllib.unescape(g['h1']), 'inLanguage': lang,
             'image': 'https://essah-urfa.de/images/web/about.jpg',
             'author': {'@type': 'Organization', 'name': 'Essah Urfa Lahmacun', 'url': 'https://essah-urfa.de/'},
             'publisher': {'@type': 'Organization', 'name': 'Essah Urfa Lahmacun', 'url': 'https://essah-urfa.de/'},
             'about': {'@id': 'https://essah-urfa.de/#restaurant'},
             'mainEntityOfPage': url},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': g['home'], 'item': home_url},
                {'@type': 'ListItem', 'position': 2, 'name': htmllib.unescape(g['og_title']), 'item': url}]},
        ]}
    alt = '\n'.join(f'<link rel="alternate" hreflang="{c}" href="https://essah-urfa.de/{"" if c == "de" else c + "/"}was-ist-lahmacun.html">' for c in ('de', 'en', 'tr'))
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{g['title']}</title>
<meta name="description" content="{g['desc']}">
<link rel="canonical" href="{url}">
{alt}
<link rel="alternate" hreflang="x-default" href="https://essah-urfa.de/was-ist-lahmacun.html">

<meta property="og:type" content="article">
<meta property="og:site_name" content="Essah Urfa Lahmacun">
<meta property="og:title" content="{g['og_title']}">
<meta property="og:description" content="{g['og_desc']}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://essah-urfa.de/images/web/about.jpg">
<meta property="og:locale" content="{g['locale']}">
<meta name="twitter:card" content="summary_large_image">

<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>

<link rel="stylesheet" href="{pre}css/style.css">
</head>
<body>

<div class="top-banner">
  <div class="section-inner top-banner-inner top-banner-inner--split">
    <a class="top-banner-social" href="https://www.instagram.com/essah_urfa/" target="_blank" rel="noopener" aria-label="{g['ig_label']}">
      {IG_SVG}
      <span>@essah_urfa</span>
    </a>
    <p class="top-banner-cross">{g['cross']}</p>
    <nav class="lang-switch" aria-label="{g['lang_label']}">
{chr(10).join(langs)}
    </nav>
  </div>
</div>

<header class="site-header" id="top">
  <div class="header-inner">
    <a href="./" class="logo">ESSAH<span>-</span>URFA</a>
    <nav class="main-nav main-nav--simple" id="mainNav">
      <a href="./">{g['nav'][0]}</a>
      <a href="./#speisekarte">{g['nav'][1]}</a>
      <a href="./#kontakt">{g['nav'][2]}</a>
    </nav>
  </div>
</header>

<main>
  <article class="legal">
    <div class="section-inner legal-inner">
      <span class="section-kicker">{g['kicker']}</span>
      <h1>{g['h1']}</h1>

      <div class="article-hero">
        <img {im('images/web/about.webp')} alt="{g['alt1']}" loading="lazy">
      </div>

      <p>{g['intro']}</p>

      <h2>{g['h2a']}</h2>
      <p>{g['pa1']}</p>
      <p>{g['pa2']}</p>

      <h2>{g['h2b']}</h2>
      <p>{g['pb']}</p>

      <h2>{g['h2c']}</h2>
      <div class="article-hero">
        <img {im('images/web/gallery-5.webp')} alt="{g['alt2']}" loading="lazy">
      </div>
      <p>{g['pc']}</p>

      <h2>{g['h2d']}</h2>
      <p>{g['pd']}</p>
    </div>
  </article>
</main>

<footer class="site-footer">
  <div class="section-inner footer-inner">
    <p>&copy; <span id="year"></span> Essah Urfa Lahmacun – Kölner Landstraße 263, 40591 Düsseldorf · <a href="https://www.instagram.com/essah_urfa/" target="_blank" rel="noopener">Instagram</a> · <a href="kiosk.html">Trinkhalle by Fero →</a></p>
    <p><a href="./">{g['foot_home']}</a> · <a href="{pre}impressum.html">{g['imp']}</a> · <a href="{pre}datenschutz.html">{g['priv']}</a></p>
  </div>
</footer>

<script src="{pre}js/script.js"></script>
</body>
</html>
'''

for lang in ('de', 'en', 'tr'):
    path = os.path.join(ROOT, ('' if lang == 'de' else lang + '/') + 'was-ist-lahmacun.html')
    open(path, 'w', encoding='utf-8').write(guide_page(lang))
print('guide pages written')


# ------------------------------------------- JSON-LD: Menu + FAQPage from visible content
def text_of(fragment):
    return re.sub(r'\s+', ' ', htmllib.unescape(re.sub(r'<[^>]+>', '', fragment))).strip()


LD_TEXT = {
    'de': ('Türkisch', 'Lahmacun-Imbiss in Düsseldorf-Wersten: handgemachter Lahmacun nach Familienrezept, dazu Döner, Pide und Pizza.'),
    'en': ('Turkish', 'Lahmacun restaurant in Düsseldorf-Wersten: handmade lahmacun from a family recipe, plus döner, pide and pizza.'),
    'tr': ('Türk mutfağı', 'Düsseldorf-Wersten’de lahmacun salonu: aile tarifiyle elde açılan lahmacun, ayrıca döner, pide ve pizza.'),
}


def enrich_index(path, page_url, lang):
    s = open(path, encoding='utf-8').read()
    sections = []
    for grp in re.findall(r'<div class="menu-group">(.*?)</div>', s, re.S):
        name = text_of(re.search(r'<h3>(.*?)</h3>', grp, re.S).group(1))
        items = []
        for n, p in re.findall(r'<span class="menu-item-name">(.*?)</span>.*?<span class="menu-item-price">(.*?)</span>', grp, re.S):
            price = text_of(p).replace('€', '').strip().replace(',', '.')
            items.append({'@type': 'MenuItem', 'name': text_of(n),
                          'offers': {'@type': 'Offer', 'price': price, 'priceCurrency': 'EUR'}})
        sections.append({'@type': 'MenuSection', 'name': name, 'hasMenuItem': items})
    menu = {'@type': 'Menu', 'url': page_url + '#speisekarte', 'hasMenuSection': sections}

    m = re.search(r'<script type="application/ld\+json">\n(.*?)\n</script>', s, re.S)
    data = json.loads(m.group(1))
    r = data['@graph'][0]
    r['hasMenu'] = menu
    r['servesCuisine'][0], r['description'] = LD_TEXT[lang]
    restaurant = '<script type="application/ld+json">\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n</script>'

    faqs = []
    for q, a in re.findall(r'<summary>(.*?)</summary>\s*<p>(.*?)</p>', s, re.S):
        faqs.append({'@type': 'Question', 'name': text_of(q),
                     'acceptedAnswer': {'@type': 'Answer', 'text': text_of(a)}})
    faq = '<script type="application/ld+json" id="ld-faq">\n' + json.dumps(
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': faqs}, ensure_ascii=False, indent=2) + '\n</script>'

    s = s[:m.start()] + restaurant + s[m.end():]
    s = re.sub(r'\n*<script type="application/ld\+json" id="ld-faq">.*?</script>', '', s, flags=re.S)
    s = s.replace(restaurant, restaurant + '\n' + faq, 1)
    open(path, 'w', encoding='utf-8').write(s)
    print(path, len(sections), 'menu sections,', len(faqs), 'FAQs')


for prefix, url, lang in (('', 'https://essah-urfa.de/', 'de'), ('en/', 'https://essah-urfa.de/en/', 'en'), ('tr/', 'https://essah-urfa.de/tr/', 'tr')):
    enrich_index(os.path.join(ROOT, prefix + 'index.html'), url, lang)
