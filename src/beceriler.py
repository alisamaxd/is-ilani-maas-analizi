"""
beceriler.py
Ortak beceri listesi. Hem anahtar kelime yontemi hem LLM AYNI listeyi kullanir,
boylece iki yontem adil karsilastirilir.

Her beceri icin:
  aciklama : LLM'e verilen kisa tanim (Ingilizce, cunku ilanlar Ingilizce)
  kalip    : anahtar kelime yonteminin arayacagi regex'ler

Listeyi veriye bakinca degistirebilirsiniz (ornegin sadece teknoloji ilanlarina
odaklanirsaniz teknik becerileri artirin). Degistirirseniz 03 ve 04'u yeniden calistirin.
"""

import re

BECERILER = {
    "python": {"aciklama": "Python programming", "kalip": [r"\bpython\b"]},
    "sql": {"aciklama": "SQL or relational databases (MySQL, PostgreSQL, etc.)",
            "kalip": [r"\bsql\b", r"\bmysql\b", r"\bpostgres(?:ql)?\b"]},
    "excel": {"aciklama": "Microsoft Excel or spreadsheets", "kalip": [r"\bexcel\b", r"\bspreadsheets?\b"]},
    "microsoft_office": {"aciklama": "Microsoft Office suite (Word, PowerPoint, Outlook)",
                         "kalip": [r"microsoft office", r"\bms office\b", r"\bpowerpoint\b", r"\boffice 365\b"]},
    "java": {"aciklama": "Java programming", "kalip": [r"\bjava\b(?!\s*script)"]},
    "javascript": {"aciklama": "JavaScript or TypeScript", "kalip": [r"\bjavascript\b", r"\btypescript\b"]},
    "cloud": {"aciklama": "Cloud platforms (AWS, Azure, Google Cloud)",
              "kalip": [r"\baws\b", r"\bazure\b", r"\bgcp\b", r"google cloud"]},
    "data_analysis": {"aciklama": "Data analysis or analytics", "kalip": [r"data analy", r"\banalytics\b"]},
    "machine_learning": {"aciklama": "Machine learning or AI", "kalip": [r"machine learning", r"\bdeep learning\b", r"\bnlp\b"]},
    "bi_tools": {"aciklama": "BI/visualization tools (Tableau, Power BI)",
                 "kalip": [r"\btableau\b", r"power ?bi\b", r"\blooker\b"]},
    "project_management": {"aciklama": "Project management", "kalip": [r"project management", r"\bpmp\b", r"project manager"]},
    "agile": {"aciklama": "Agile or Scrum methods", "kalip": [r"\bagile\b", r"\bscrum\b", r"\bkanban\b"]},
    "communication": {"aciklama": "Communication skills (written or verbal)",
                      "kalip": [r"communication skills?", r"communicate effectively", r"verbal and written"]},
    "leadership": {"aciklama": "Leadership or team management", "kalip": [r"\bleadership\b", r"manage a team", r"team lead"]},
    "teamwork": {"aciklama": "Teamwork or collaboration", "kalip": [r"\bteamwork\b", r"team player", r"\bwork(?:s|ing)?\s+(?:well\s+)?(?:as part of|in|within|with)\s+(?:a\s+)?team", r"collaborat\w+\s+with"]},
    "customer_service": {"aciklama": "Customer service or support", "kalip": [r"customer service", r"customer support"]},
    "sales": {"aciklama": "Sales experience", "kalip": [r"\bsales\b", r"business development"]},
    "negotiation": {"aciklama": "Negotiation", "kalip": [r"negotiat"]},
    "marketing": {"aciklama": "Marketing (digital, content, SEO, etc.)", "kalip": [r"\bmarketing\b", r"\bseo\b"]},
    "accounting": {"aciklama": "Accounting, bookkeeping or CPA", "kalip": [r"\baccounting\b", r"bookkeeping", r"\bcpa\b"]},
    "finance_budget": {"aciklama": "Financial analysis, budgeting or forecasting",
                       "kalip": [r"financial analysis", r"\bbudget", r"forecasting"]},
    "spanish": {"aciklama": "Spanish or bilingual ability", "kalip": [r"\bspanish\b", r"\bbilingual\b"]},
    "cpr_bls": {"aciklama": "CPR / BLS / ACLS certification", "kalip": [r"\bcpr\b", r"\bbls\b", r"\bacls\b"]},
    "nursing": {"aciklama": "Nursing license or nursing experience (RN, LPN)",
                "kalip": [r"registered nurse", r"\brn\b", r"\blpn\b"]},
    "driver_cdl": {"aciklama": "Driver's license or CDL", "kalip": [r"\bcdl\b", r"driver'?s license", r"driving record"]},
    "forklift": {"aciklama": "Forklift or warehouse equipment", "kalip": [r"forklift", r"pallet jack"]},
    "quality": {"aciklama": "Quality assurance or quality control", "kalip": [r"quality assurance", r"quality control", r"\bqa\b"]},
    "crm": {"aciklama": "CRM tools (Salesforce, HubSpot)", "kalip": [r"\bcrm\b", r"salesforce", r"hubspot"]},
    "erp_sap": {"aciklama": "ERP systems (SAP, Oracle)", "kalip": [r"\bsap\b", r"\berp\b", r"\boracle\b"]},
    "social_media": {"aciklama": "Social media management", "kalip": [r"social media"]},
    "writing": {"aciklama": "Writing or editing", "kalip": [r"\bwriting\b", r"\bediting\b", r"copywriting"]},
    "research": {"aciklama": "Research skills", "kalip": [r"\bresearch\b"]},
    "training": {"aciklama": "Training or mentoring others", "kalip": [r"\btrain(?:ing)?\s+(?:of\s+)?(?:new|junior|staff|team|others|employees)", r"\bmentor", r"\bcoach(?:ing)?\b"]},
    "problem_solving": {"aciklama": "Problem solving or critical thinking", "kalip": [r"problem[- ]solving", r"critical thinking"]},
    "time_management": {"aciklama": "Time management or organization", "kalip": [r"time management", r"\borganizational skills\b"]},
    "attention_to_detail": {"aciklama": "Attention to detail", "kalip": [r"attention to detail", r"detail[- ]oriented"]},
    "bachelors": {"aciklama": "Bachelor's degree required or preferred", "kalip": [r"bachelor", r"\bb\.?s\.? degree\b"]},
    "masters": {"aciklama": "Master's degree or higher required or preferred", "kalip": [r"master'?s", r"\bphd\b", r"\bmba\b"]},
    "security_clearance": {"aciklama": "Security clearance", "kalip": [r"security clearance", r"\bsecret clearance\b"]},
     "recruiting_hr": {"aciklama": "Recruiting or human resources", "kalip": [r"\brecruiters?\b", r"talent acquisition", r"\bhris\b", r"human resources\s+(?:experience|generalist|manager|coordinator)"]},
}

BECERI_ADLARI = list(BECERILER.keys())

# "R" programlama dili buyuk/kucuk harfe duyarli aranmali, yoksa her "r" harfini yakalar
_R_KALIBI = re.compile(r"(?<![A-Za-z0-9+#.])R(?![A-Za-z0-9+#&/])")

_DERLENMIS = {
    ad: [re.compile(k, re.IGNORECASE) for k in b["kalip"]]
    for ad, b in BECERILER.items()
}


def anahtar_kelime_cikar(metin):
    """Metinde gecen becerilerin ad listesini dondurur (anahtar kelime yontemi)."""
    if not isinstance(metin, str) or not metin.strip():
        return []
    bulunan = [ad for ad, kaliplar in _DERLENMIS.items() if any(k.search(metin) for k in kaliplar)]
    if _R_KALIBI.search(metin):
        bulunan.append("r_language")
    return bulunan


# r_language, BECERI_ADLARI'na da eklenir (kolon seti sabit kalsin diye)
BECERILER["r_language"] = {"aciklama": "R programming language (statistics)", "kalip": []}
BECERI_ADLARI = list(BECERILER.keys())
