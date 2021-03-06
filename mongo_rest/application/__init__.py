# -*- coding: utf-8 -*-
"""Application Initializer Module

This module consist of application and application level attributes
like ``db`` as database object.

Attributes:
    ROOT_DIR (str): This variable store absolute path of
        root dir of application.
"""
# Version of the application.
__version__ = "0.1"

# This lib. provides safe threading. For more information: http://eventlet.net/
import eventlet

# System library.
import sys

# Monkey patching is for multi-threading with Flask requests.
if sys.version_info[1] > 6:  # If python version is greater then 3.6
    # This is done because there is some incompatibles with eventlet
    # with greater version of Python 3.6
    eventlet.monkey_patch(os=False)
else:
    eventlet.monkey_patch()

# Operating system library.
import os

# Store path of application root in a variable.
ROOT_DIR = os.path.join(os.path.dirname(__file__), "..")

# Import logging library.
# More about loguru: https://loguru.readthedocs.io/en/stable/overview.html
from loguru import logger

# Remove default handler.
logger.remove()

# Console logger.
logger.add(sink=sys.stderr, level=os.environ.get("CONSOLE_LOG_LEVEL", "INFO"),
           format="|{time}| |{process}| |{level}| |{name}:{function}:{line}| "
                  "{message}")

# File logger.
logger.add(sink=os.path.join(ROOT_DIR, "logs", "log_{time}.log"),
           serialize=True,
           rotation="10 MB",  # Every log file max size.
           # Remove logs older than 3 days.
           retention="3 days", level=os.environ.get("FILE_LOG_LEVEL", "DEBUG"))

# Create database instance.
from flask_pymongo import MongoClient
db = MongoClient(os.getenv("MONGO_URI"))["univerdustry"]

# Create application instance.
from application.factory import create_app
app = create_app()

# NOTE: This only for development, remove on production.
try:
    db["organization"].insert_many([
        {'name': 'Abdullah Gül Üniversitesi', 'domain': 'agu.edu.tr'},
        {'name': 'Adana Alparslan Türkeş Bilim ve Teknoloji Üniversitesi', 'domain': 'atu.edu.tr'},
        {'name': 'Adıyaman Üniversitesi', 'domain': 'adiyaman.edu.tr'},
        {'name': 'Afyon Kocatepe Üniversitesi', 'domain': 'aku.edu.tr'},
        {'name': 'Afyonkarahisar Sağlık Bilimleri Üniversitesi', 'domain': 'afsu.edu.tr'},
        {'name': 'Akdeniz Üniversitesi', 'domain': 'akdeniz.edu.tr'},
        {'name': 'Aksaray Üniversitesi', 'domain': 'aksaray.edu.tr'},
        {'name': 'Alanya Alaaddin Keykubat Üniversitesi', 'domain': 'alanya.edu.tr'},
        {'name': 'Amasya Üniversitesi', 'domain': 'amasya.edu.tr'},
        {'name': 'Anadolu Üniversitesi', 'domain': 'anadolu.edu.tr'},
        {'name': 'Ankara Hacı Bayram Veli Üniversitesi', 'domain': 'ahbv.edu.tr'},
        {'name': 'Ankara Müzik ve Güzel Sanatlar Üniversitesi', 'domain': 'mgu.edu.tr'},
        {'name': 'Ankara Sosyal Bilimler Üniversitesi', 'domain': 'asbu.edu.tr'},
        {'name': 'Ankara Yıldırım Beyazıt Üniversitesi', 'domain': 'aybu.edu.tr'},
        {'name': 'Ankara Üniversitesi', 'domain': 'ankara.edu.tr'},
        {'name': 'Ardahan Üniversitesi', 'domain': 'ardahan.edu.tr'},
        {'name': 'Artvin Çoruh Üniversitesi', 'domain': 'artvin.edu.tr'},
        {'name': 'Atatürk Üniversitesi', 'domain': 'atauni.edu.tr'},
        {'name': 'Aydın Adnan Menderes Üniversitesi', 'domain': 'adu.edu.tr'},
        {'name': 'Ağrı İbrahim Çeçen Üniversitesi', 'domain': 'agri.edu.tr'},
        {'name': 'Balıkesir Üniversitesi', 'domain': 'balikesir.edu.tr'},
        {'name': 'Bandırma Onyedi Eylül Üniversitesi', 'domain': 'bandirma.edu.tr'},
        {'name': 'Bartın Üniversitesi', 'domain': 'bartin.edu.tr'},
        {'name': 'Batman Üniversitesi', 'domain': 'batman.edu.tr'},
        {'name': 'Bayburt Üniversitesi', 'domain': 'bayburt.edu.tr'},
        {'name': 'Bilecik Şeyh Edebali Üniversitesi', 'domain': 'bilecik.edu.tr'},
        {'name': 'Bingöl Üniversitesi', 'domain': 'bingol.edu.tr'},
        {'name': 'Bitlis Eren Üniversitesi', 'domain': 'bitliseren.edu.tr'},
        {'name': 'Bolu Abant İzzet Baysal Üniversitesi', 'domain': 'ibu.edu.tr'},
        {'name': 'Boğaziçi Üniversitesi', 'domain': 'boun.edu.tr'},
        {'name': 'Burdur Mehmet Akif Ersoy', 'domain': 'mehmetakif.edu.tr'},
        {'name': 'Bursa Teknik Üniversitesi', 'domain': 'btu.edu.tr'},
        {'name': 'Bursa Uludağ Üniversitesi', 'domain': 'uludag.edu.tr'},
        {'name': 'Çanakkale Onsekiz Mart Üniversitesi', 'domain': 'comu.edu.tr'},
        {'name': 'Çankırı Karatekin Üniversitesi', 'domain': 'karatekin.edu.tr'},
        {'name': 'Çukurova Üniversitesi', 'domain': 'cu.edu.tr'},
        {'name': 'Dicle Üniversitesi', 'domain': 'dicle.edu.tr'},
        {'name': 'Dokuz Eylül Üniversitesi', 'domain': 'deu.edu.tr'},
        {'name': 'Düzce Üniversitesi', 'domain': 'duzce.edu.tr'},
        {'name': 'Ege Üniversitesi', 'domain': 'ege.edu.tr'},
        {'name': 'Erciyes Üniversitesi', 'domain': 'erciyes.edu.tr'},
        {'name': 'Erzincan Binali Yıldırım Üniversitesi', 'domain': 'ebyu.edu.tr'},
        {'name': 'Erzurum Teknik Üniversitesi', 'domain': 'erzurum.edu.tr'},
        {'name': 'Eskişehir Osmangazi Üniversitesi', 'domain': 'ogu.edu.tr'},
        {'name': 'Eskişehir Teknik Üniversitesi', 'domain': 'eskisehir.edu.tr'},
        {'name': 'Fırat Üniversitesi', 'domain': 'firat.edu.tr'},
        {'name': 'Galatasaray Üniversitesi', 'domain': 'gsu.edu.tr'},
        {'name': 'Gazi Üniversitesi', 'domain': 'gazi.edu.tr'},
        {'name': 'Gaziantep Bilim ve Teknoloji Üniversitesi', 'domain': 'gibtu.net'},
        {'name': 'Gaziantep Üniversitesi', 'domain': 'gantep.edu.tr'},
        {'name': 'Gebze Teknik Üniversitesi', 'domain': 'gtu.edu.tr'},
        {'name': 'Giresun Üniversitesi', 'domain': 'giresun.edu.tr'},
        {'name': 'Gümüşhane Üniversitesi', 'domain': 'gumushane.edu.tr'},
        {'name': 'Hacettepe Üniversitesi', 'domain': 'hacettepe.edu.tr'},
        {'name': 'Hakkari Üniversitesi', 'domain': 'hakkari.edu.tr'},
        {'name': 'Harran Üniversitesi', 'domain': 'harran.edu.tr'},
        {'name': 'Hatay Mustafa Kemal Üniversitesi', 'domain': 'mku.edu.tr'},
        {'name': 'Hitit Üniversitesi', 'domain': 'hitit.edu.tr'},
        {'name': 'Isparta Uygulamalı Bilimler Üniversitesi', 'domain': 'isparta.edu.tr'},
        {'name': 'Iğdır Üniversitesi', 'domain': 'igdir.edu.tr'},
        {'name': 'İnönü Üniversitesi', 'domain': 'inonu.edu.tr'},
        {'name': 'İskenderun Tenik Üniversitesi', 'domain': 'iste.edu.tr'},
        {'name': 'İstanbul Medeniyet Üniversitesi', 'domain': 'medeniyet.edu.tr'},
        {'name': 'İstanbul Teknik Üniversitesi', 'domain': 'itu.edu.tr'},
        {'name': 'İstanbul Üniversitesi', 'domain': 'istanbul.edu.tr'},
        {'name': 'İstanbul Üniversitesi-Cerrahpaşa', 'domain': 'istanbulc.edu.tr'},
        {'name': 'İzmir Bakırçay Üniversitesi', 'domain': 'bakircay.edu.tr'},
        {'name': 'İzmir Demokrasi Üniversitesi', 'domain': 'idu.edu.tr'},
        {'name': 'İzmir Katip Çelebi Üniversitesi', 'domain': 'ikc.edu.tr'},
        {'name': 'İzmir Yüksek Teknoloji Enstitüsü', 'domain': 'iyte.edu.tr'},
        {'name': 'Kafkas Üniversitesi', 'domain': 'kafkas.edu.tr'},
        {'name': 'Kahramanmaraş İstiklal Üniversitesi', 'domain': 'istiklal.edu.tr'},
        {'name': 'Kahramanmaraş Sütçü İmam Üniversitesi', 'domain': 'ksu.edu.tr'},
        {'name': 'Karabük Üniversitesi', 'domain': 'karabuk.edu.tr'},
        {'name': 'Karadeniz Teknik Üniversitesi', 'domain': 'ktu.edu.tr'},
        {'name': 'Karamanoğlu Mehmetbey Üniversitesi', 'domain': 'kmu.edu.tr'},
        {'name': 'Kastamonu Üniversitesi', 'domain': 'kastamonu.edu.tr'},
        {'name': 'Kayseri Üniversitesi', 'domain': 'kayseri.edu.tr'},
        {'name': 'Kilis 7 Aralık Üniversitesi', 'domain': 'kilis.edu.tr'},
        {'name': 'Kocaeli Üniversitesi', 'domain': 'kocaeli.edu.tr'},
        {'name': 'Konya Teknik Üniversitesi', 'domain': 'ktun.edu.tr'},
        {'name': 'Kütahya Dumlupınar Üniversitesi', 'domain': 'dumlupinar.edu.tr'},
        {'name': 'Kütahya Sağlık Bilimleri Üniversitesi', 'domain': 'ksbu.edu.tr'},
        {'name': 'Kırıkkale Üniversitesi', 'domain': 'kku.edu.tr'},
        {'name': 'Kırklareli Üniversitesi', 'domain': 'klu.edu.tr'},
        {'name': 'Kırşehir Ahi Evran Üniversitesi', 'domain': 'ahievran.edu.tr'},
        {'name': 'Malatya Turgut Özal Üniversitesi', 'domain': 'ozal.edu.tr'},
        {'name': 'Manisa Celal Bayar Üniversitesi', 'domain': 'mcbu.edu.tr'},
        {'name': 'Mardin Artuklu Üniversitesi', 'domain': 'artuklu.edu.tr'},
        {'name': 'Marmara Üniversitesi', 'domain': 'marmara.edu.tr'},
        {'name': 'Mersin Üniversitesi', 'domain': 'mersin.edu.tr'},
        {'name': 'Mimar Sinan Güzel Sanatlar Üniversitesi', 'domain': 'msgsu.edu.tr'},
        {'name': 'Muğla Sıtkı Koçman Üniversitesi', 'domain': 'mu.edu.tr'},
        {'name': 'Munzur Üniversitesi', 'domain': 'munzur.edu.tr'},
        {'name': 'Muş Alparslan Üniversitesi', 'domain': 'alparslan.edu.tr'},
        {'name': 'Necmettin Erbakan Üniversitesi', 'domain': 'erbakan.edu.tr'},
        {'name': 'Nevşehir Hacı Bektaş Veli Üniversitesi', 'domain': 'nevsehir.edu.tr'},
        {'name': 'Niğde Ömer Halidemir Üniversitesi', 'domain': 'ohu.edu.tr'},
        {'name': 'Ondokuz Mayıs Üniversitesi', 'domain': 'omu.edu.tr'},
        {'name': 'Ordu Üniversitesi', 'domain': 'odu.edu.tr'},
        {'name': 'Orta Doğu Teknik Üniversitesi', 'domain': 'metu.edu.tr'},
        {'name': 'Osmaniye Korkut Ata Üniversitesi', 'domain': 'osmaniye.edu.tr'},
        {'name': 'Pamukkale Üniversitesi', 'domain': 'pau.edu.tr'},
        {'name': 'Recep Tayyip Erdoğan Üniversitesi', 'domain': 'erdogan.edu.tr'},
        {'name': 'Sağlık Bilimleri Üniversitesi', 'domain': 'sbu.edu.tr'},
        {'name': 'Sakarya Uygulamalı Bilimler Üniversitesi', 'domain': 'subu.edu.tr'},
        {'name': 'Sakarya Üniversitesi', 'domain': 'sakarya.edu.tr'},
        {'name': 'Samsun Üniversitesi', 'domain': 'samsun.edu.tr'},
        {'name': 'Selçuk Üniversitesi', 'domain': 'selcuk.edu.tr'},
        {'name': 'Siirt Üniversitesi', 'domain': 'siirt.edu.tr'},
        {'name': 'Sinop Üniversitesi', 'domain': 'sinop.edu.tr'},
        {'name': 'Sivas Cumhuriyet Üniversitesi', 'domain': 'cumhuriyet.edu.tr'},
        {'name': 'Süleyman Demirel Üniversitesi', 'domain': 'sdu.edu.tr'},
        {'name': 'Şırnak Üniversitesi', 'domain': 'sirnak.edu.tr'},
        {'name': 'Tarsus Üniversitesi', 'domain': 'tarsus.edu.tr'},
        {'name': 'Tekirdağ Namık Kemal Üniversitesi', 'domain': 'nku.edu.tr'},
        {'name': 'Tokat Gaziosmanpaşa Üniversitesi', 'domain': 'gop.edu.tr'},
        {'name': 'Trabzon Üniversitesi', 'domain': 'trabzon.edu.tr'},
        {'name': 'Trakya Üniversitesi', 'domain': 'trakya.edu.tr'},
        {'name': 'Türk-Alman Üniversitesi', 'domain': 'tau.edu.tr'},
        {'name': 'Uşak Üniversitesi', 'domain': 'usak.edu.tr'},
        {'name': 'Van Yüzüncü Yıl Üniversitesi', 'domain': 'yyu.edu.tr'},
        {'name': 'Yalova Üniversitesi', 'domain': 'yalova.edu.tr'},
        {'name': 'Yıldız Teknik Üniversitesi', 'domain': 'yildiz.edu.tr'},
        {'name': 'Yozgat Bozok Üniversitesi', 'domain': 'bozok.edu.tr'},
        {'name': 'Zonguldak Bülent Ecevit Üniversitesi', 'domain': 'beun.edu.tr'},
        {'name': 'Acıbadem Mehmet Ali Aydınlar Üniversitesi', 'domain': 'acibadem.edu.tr'},
        {'name': 'Alanya Hamdullah Emin Paşa Üniversitesi', 'domain': 'ahep.edu.tr'},
        {'name': 'Altınbaş Üniversitesi', 'domain': 'altinbas.edu.tr'},
        {'name': 'Anka Teknoloji Üniversitesi', 'domain': 'anka.edu.tr'},
        {'name': 'Antalya AKEV Üniversitesi', 'domain': 'akev.edu.tr'},
        {'name': 'Antalya Bilim Üniversitesi', 'domain': 'antalya.edu.tr'},
        {'name': 'Ataşehir Adıgüzel Meslek Yüksekokulu', 'domain': 'adiguzel.edu.tr'},
        {'name': 'Atılım Üniversitesi', 'domain': 'atilim.edu.tr'},
        {'name': 'Avrasya Üniversitesi', 'domain': 'avrasya.edu.tr'},
        {'name': 'Avrupa Meslek Yüksekokulu', 'domain': 'avrupa.edu.tr'},
        {'name': 'Bahçeşehir Üniversitesi', 'domain': 'bau.edu.tr'},
        {'name': 'Başkent Üniversitesi', 'domain': 'baskent.edu.tr'},
        {'name': 'Beykent Üniversitesi', 'domain': 'beykent.edu.tr'},
        {'name': 'Beykoz Üniversitesi', 'domain': 'beykoz.edu.tr'},
        {'name': 'Bezmiâlem Vakıf Üniversitesi', 'domain': 'bezmialem.edu.tr'},
        {'name': 'Biruni Üniversitesi', 'domain': 'biruni.edu.tr'},
        {'name': 'Çağ Üniversitesi', 'domain': 'cag.edu.tr'},
        {'name': 'Çankaya Üniversitesi', 'domain': 'cankaya.edu.tr'},
        {'name': 'Doğuş Üniversitesi', 'domain': 'dogus.edu.tr'},
        {'name': 'Faruk Saraç Tasarım Meslek Yüksekokulu', 'domain': 'faruksarac.edu.tr'},
        {'name': 'Fatih Sultan Mehmet Vakıf Üniversitesi', 'domain': 'fatihsultan.edu.tr'},
        {'name': 'Fenerbahçe Üniversitesi', 'domain': 'fbu.edu.tr'},
        {'name': 'Haliç Üniversitesi', 'domain': 'halic.edu.tr'},
        {'name': 'Hasan Kalyoncu Üniversitesi', 'domain': 'hku.edu.tr'},
        {'name': 'Işık Üniversitesi', 'domain': 'isikun.edu.tr'},
        {'name': 'İhsan Doğramacı Bilkent Üniversitesi', 'domain': 'bilkent.edu.tr'},
        {'name': 'İstanbul 29 Mayıs Üniversitesi', 'domain': '29mayis.edu.tr'},
        {'name': 'İstanbul Arel Üniversitesi', 'domain': 'arel.edu.tr'},
        {'name': 'İstanbul Atlas Üniversitesi', 'domain': 'atlas.edu.tr'},
        {'name': 'İstanbul Aydın Üniversitesi', 'domain': 'aydin.edu.tr'},
        {'name': 'İstanbul Ayvansaray Üniversitesi', 'domain': 'ayvansaray.edu.tr'},
        {'name': 'İstanbul Bilgi Üniversitesi', 'domain': 'bilgi.edu.tr'},
        {'name': 'İstanbul Bilim Üniversitesi', 'domain': 'istanbulbilim.edu.tr'},
        {'name': 'İstanbul Esenyurt Üniversitesi', 'domain': 'esenyurt.edu.tr'},
        {'name': 'İstanbul Gedik Üniversitesi', 'domain': 'gedik.edu.tr'},
        {'name': 'İstanbul Gelişim Üniversitesi', 'domain': 'gelisim.edu.tr'},
        {'name': 'İstanbul İbn Haldun Üniversitesi', 'domain': 'ihu.edu.tr'},
        {'name': 'İstanbul Kent Üniversitesi', 'domain': 'kent.edu.tr'},
        {'name': 'İstanbul Kültür Üniversitesi', 'domain': 'iku.edu.tr'},
        {'name': 'İstanbul Medipol Üniversitesi', 'domain': 'medipol.edu.tr'},
        {'name': 'İstanbul Okan Üniversitesi', 'domain': 'okan.edu.tr'},
        {'name': 'İstanbul Rumeli Üniversitesi', 'domain': 'umeli.edu.tr'},
        {'name': 'İstanbul Sabahattin Zaim Üniversitesi', 'domain': 'izu.edu.tr'},
        {'name': 'İstanbul Şehir Üniversitesi', 'domain': 'sehir.edu.tr'},
        {'name': 'İstanbul Şişli Meslek Yüksekokulu', 'domain': 'sisli.edu.tr'},
        {'name': 'İstanbul Ticaret Üniversitesi', 'domain': 'ticaret.edu.tr'},
        {'name': 'İstanbul Yeni Yüzyıl Üniversitesi', 'domain': 'yeniyuzyil.edu.tr'},
        {'name': 'İstinye Üniversitesi', 'domain': 'istinye.edu.tr'},
        {'name': 'İzmir Ekonomi Üniversitesi', 'domain': 'ieu.edu.tr'},
        {'name': 'İzmir Tınaztepe Üniversitesi', 'domain': 'tinaztepe.edu.tr'},
        {'name': 'Kadir Has Üniversitesi', 'domain': 'khas.edu.tr'},
        {'name': 'Kapadokya Üniversitesi', 'domain': 'kapadokya.edu.tr'},
        {'name': 'Kavram Meslek Yüksekokulu', 'domain': 'kavram.edu.tr'},
        {'name': 'Koç Üniversitesi', 'domain': 'ku.edu.tr'},
        {'name': 'Konya Gıda ve Tarım Üniversitesi', 'domain': 'gidatarim.edu.tr'},
        {'name': 'KTO Karatay Üniversitesi', 'domain': 'karatay.edu.tr'},
        {'name': 'Lokman Hekim Üniversitesi', 'domain': 'lokmanhekim.edu.tr'},
        {'name': 'Maltepe Üniversitesi', 'domain': 'maltepe.edu.tr'},
        {'name': 'MEF Üniversitesi', 'domain': 'mef.edu.tr'},
        {'name': 'Nişantaşı Üniversitesi', 'domain': 'nisantasi.edu.tr'},
        {'name': 'Nuh Naci Yazgan Üniversitesi', 'domain': 'nny.edu.tr'},
        {'name': 'Ostim Teknik Üniversitesi', 'domain': 'ostimteknik.edu.tr'},
        {'name': 'Özyeğin Üniversitesi', 'domain': 'ozyegin.edu.tr'},
        {'name': 'Piri Reis Üniversitesi', 'domain': 'pirireis.edu.tr'},
        {'name': 'Sabancı Üniversitesi', 'domain': 'sabanciuniv.edu'},
        {'name': 'Sanko Üniversitesi', 'domain': 'sanko.edu.tr'},
        {'name': 'TED Üniversitesi', 'domain': 'tedu.edu.tr'},
        {'name': 'TOBB Ekonomi ve Teknoloji Üniversitesi', 'domain': 'etu.edu.tr'},
        {'name': 'Toros Üniversitesi', 'domain': 'toros.edu.tr'},
        {'name': 'Türk Hava Kurumu Üniversitesi', 'domain': 'thk.org.tr'},
        {'name': 'Ufuk Üniversitesi', 'domain': 'ufuk.edu.tr'},
        {'name': 'Üsküdar Üniversitesi', 'domain': 'uskudar.edu.tr'},
        {'name': 'Yaşar Üniversitesi', 'domain': 'yasar.edu.tr'},
        {'name': 'Yeditepe Üniversitesi', 'domain': 'yeditepe.edu.tr'},
        {'name': 'Yüksek İhtisas Üniversitesi', 'domain': 'yuksekihtisasuniversitesi.edu.tr'}
    ])
except Exception:
    pass
