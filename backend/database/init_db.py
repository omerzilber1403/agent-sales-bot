from .connection import init_db as _create_tables, SessionLocal
from ..models.company import Company
import secrets


def init_db():
    """Initialize database tables (creates all schema if not exists)."""
    _create_tables()


def _upsert_company(db, domain: str, defaults: dict) -> bool:
    """Insert or update company by domain. Returns True if inserted, False if updated."""
    existing = db.query(Company).filter(Company.domain == domain).first()
    if existing:
        for key, value in defaults.items():
            setattr(existing, key, value)
        db.commit()
        return False
    company = Company(api_key=f"ak_{secrets.token_urlsafe(32)}", **defaults)
    db.add(company)
    db.commit()
    return True


def seed_demo_company():
    """Forcepoint — real enterprise data security B2B company (Antigravity data)."""
    db = SessionLocal()
    try:
        inserted = _upsert_company(db, "forcepoint.com", dict(
            name="Forcepoint",
            domain="forcepoint.com",
            locale="he-IL",
            timezone="UTC",
            currency="USD",
            business_type="B2B",
            one_line_value=(
                "ה-Data Security Cloud של Forcepoint מגן על מידע רגיש בכל מקום — "
                "נקודות קצה, ענן, אינטרנט, אימייל ו-GenAI — מפלטפורמה מאוחדת אחת המבוססת על AI."
            ),
            brand_voice={
                "style": "authoritative, data-first, enterprise-grade, technically precise, confident",
                "closing_tone": "schedule_demo",
                "avoid": (
                    "consumer language, fear-mongering without solutions, "
                    "vague buzzwords without technical grounding, "
                    "discussion of price/cost sensitivity"
                ),
            },
            icp={
                "company_size": "ארגונים בינוניים וגדולים; סוכנויות ממשלתיות ותחומים מפוקחים בכל הגדלים",
                "industries": [
                    "ממשלה וביטחון", "שירותים פיננסיים ובנקאות", "בריאות",
                    "אנרגיה ושירותים ציבוריים", "תשתיות קריטיות", "ייצור",
                    "תעשיית האוויר והחלל", "טכנולוגיית מידע", "בידור",
                ],
                "buyer_roles": [
                    "CISO (Chief Information Security Officer)", "VP of Security",
                    "Director of Information Security", "IT Security Manager",
                    "Compliance Officer", "Data Protection Officer (DPO)", "CIO",
                ],
                "pain_trigger": (
                    "סיכון חשיפת מידע בלתי מבוקרת בסביבות היברידיות ומרוחקות, אימוץ GenAI, "
                    "ומעבר לענן — מוחמר על ידי איומים פנימיים, דרישות ציות ופיזור כלים."
                ),
            },
            pain_points=[
                "אובדן נראות ושליטה על מידע רגיש כשהוא עובר בין אפליקציות ענן, נקודות קצה, אימייל ופלטפורמות GenAI",
                "חוסר יכולת לאתר ולעצור איומים פנימיים — עובדים זדוניים ורשלניים — לפני דליפת המידע",
                "ניהול כלי אבטחה מנותקים רבים מדי עם מדיניות חופפת ובלי קונסולה מאוחדת",
                "כישלון בביקורות ציות בשל חוסר יכולת לגלות, לסווג ולנטר מידע מוסדר (HIPAA, GDPR, CMMC)",
                "עומס על צוותי אבטחה מ-False Positives ועייפות-התרעות ממערכות DLP ישנות חסרות הקשר התנהגותי",
            ],
            products=[
                {
                    "id": "forcepoint_one_sse",
                    "name": "Forcepoint ONE SSE (Security Service Edge)",
                    "summary": "פלטפורמת SSE ענן-native המאחדת SWG, CASB, ZTNA ו-DLP תחת מנוע מדיניות אחד.",
                    "base_price": "פנה לקבלת מחיר",
                    "details": (
                        "מספקת הגנת איומים מתקדמת ואבטחת מידע ארגונית מהענן. "
                        "משלבת SWG, CASB, RBI ו-ZTNA עם מנוע ה-DLP של Forcepoint תחת קונסולה אחת. "
                        "תמיכה ב-BYOD ללא Agent. "
                        "הוכרה כ-Leader ב-Forrester Wave: SSE Q1 2024 "
                        "ו-Gartner Peer Insights Customers' Choice 2024 עם 98% המלצה."
                    ),
                    "addons": "Remote Browser Isolation (RBI), מודול ZTNA, Data-first SASE עם Forcepoint FlexEdge Secure SD-WAN",
                },
                {
                    "id": "forcepoint_dlp",
                    "name": "Forcepoint Data Loss Prevention (DLP)",
                    "summary": "פתרון DLP מוביל המשתמש ב-AI לגילוי, סיווג, ניטור ואכיפת מדיניות הגנת מידע בדואל אלקטרוני, אינטרנט, ענן ונקודות קצה.",
                    "base_price": "פנה לקבלת מחיר",
                    "details": (
                        "טכנולוגיית AI Mesh מזהה מידע מובנה ולא-מובנה בקנה מידה. "
                        "תבניות מובנות ל-GDPR, HIPAA, PCI-DSS, CMMC ומאות תקנות. "
                        "Frost & Sullivan 2024 Global DLP Company of the Year (שנה שנייה ברציפות). "
                        "Leader ב-IDC MarketScape: Worldwide DLP 2025."
                    ),
                    "addons": "מודול Risk-Adaptive Protection, סוכן DLP לנקודות קצה, DLP לדואר אלקטרוני",
                },
                {
                    "id": "forcepoint_dspm",
                    "name": "Forcepoint Data Security Posture Management (DSPM)",
                    "summary": "DSPM מבוסס AI המספק נראות בזמן אמת לסיכוני מידע בסביבות ענן מרובות עם תיקון אוטומטי.",
                    "base_price": "פנה לקבלת מחיר",
                    "details": (
                        "משתמש ב-AI Mesh לסריקת אחסון ענן מרובה — מזהה קבצים מיושנים, גישה בלתי תקינה וחשיפה לא ידועה. "
                        "Data Detection and Remediation (DDR) מבוסס AI מאפשר הפחתת סיכונים אוטומטית. "
                        "משתלב עם Forcepoint DLP להגנת מידע מלאה."
                    ),
                    "addons": "Data Detection and Remediation (DDR), שילוב עם Forcepoint DLP ו-Forcepoint ONE",
                },
                {
                    "id": "forcepoint_one_data_security",
                    "name": "Forcepoint ONE Data Security",
                    "summary": "פלטפורמה מאוחדת מהענן המאכפת מדיניות DLP יחידה בנקודות קצה, אינטרנט, ענן ודואר אלקטרוני מקונסולה אחת.",
                    "base_price": "פנה לקבלת מחיר",
                    "details": (
                        "מבטלת מוצרי DLP מרובים על ידי אכיפת מדיניות עקבית בכל הערוצים. "
                        "קונסולה אחת, כיסוי BYOD ללא Agent, תגובה מהירה לאירועים. "
                        "מפחיתה עלויות תפעוליות בעד 31% תוך שיפור פרודוקטיביות הצוות."
                    ),
                    "addons": "מודול GenAI Security, שילוב אבטחת דואל אלקטרוני, שילוב CASB",
                },
                {
                    "id": "forcepoint_genai_security",
                    "name": "Forcepoint GenAI Security",
                    "summary": "נראות ושליטה על שימוש עובדים באפליקציות GenAI — מניעת דליפת מידע רגיש דרך פרומפטים והעלאות.",
                    "base_price": "פנה לקבלת מחיר",
                    "details": (
                        "מאפשר אימוץ בטוח של כלי GenAI (ChatGPT, Copilot, Gemini) ללא סיכון מידע. "
                        "מנטר ושולט בפרומפטים, העלאות קבצים ומידע שמשותף עם פלטפורמות AI. "
                        "מסופק דרך Forcepoint ONE SSE; משתלב עם מדיניות DLP קיימת, אין צורך בתשתית חדשה. "
                        "מספק מסלולי ביקורת מלאים ותיעוד ציות לאירועי מידע הקשורים ל-AI."
                    ),
                    "addons": "בנוי על Forcepoint ONE SSE; משתלב עם Forcepoint DLP",
                },
                {
                    "id": "forcepoint_ngfw",
                    "name": "Forcepoint Next Generation Firewall (NGFW)",
                    "summary": "אבטחת רשת ארגונית עם מניעת איומים מתקדמת ותעודות ממשלתיות לסביבות תשתית קריטית ומבוזרת.",
                    "base_price": "פנה לקבלת מחיר",
                    "details": (
                        "הגנת high-availability עם זיהוי פרצות מתקדם, IPS, בדיקת תנועה מוצפנת, הפרדת OT/IT. "
                        "תעודות: Common Criteria (NIAP), FIPS 140-3 Level 2, DoDIN APL. "
                        "תומך ב-NERC-CIP ו-ISA/IEC 62443 לאנרגיה ותשתיות קריטיות."
                    ),
                    "addons": "Forcepoint Data Guard (אימות נתוני OT/IT), מודול IPS, שילוב FlexEdge SD-WAN",
                },
            ],
            differentiators=[
                "טכנולוגיית AI Mesh — AI מרובה-מודלים קנייני לסיווג מידע בזמן אמת בכל הפורמטים והמיקומים",
                "Risk-Adaptive Protection — מתאים אכיפת DLP בדינמיות לפי התנהגות המשתמש וציון הסיכון האישי בזמן אמת",
                "פלטפורמת 'Data Security Everywhere' מאוחדת — מנוע מדיניות אחד, קונסולה אחת לנקודות קצה, אינטרנט, אימייל, ענן ו-GenAI",
                "200+ מרכזי נתונים עולמיים עם SLA זמינות של 99.99%",
            ],
            competitors_map={
                "Netskope": (
                    "Forcepoint ממוקד יותר במידע. ה-DLP משולב באופן נטיבי — לא מוצמד — "
                    "עם דיוק סיווג AI Mesh. Risk-Adaptive Protection הוא אינטליגנציה התנהגותית ייחודית שאין ל-Netskope."
                ),
                "Zscaler": (
                    "'Data-first' מול 'access-first' של Zscaler. ה-DLP של Zscaler פחות בשל. "
                    "Forcepoint מכוון לקונים שמעדיפים תוצאות הגנת מידע על אבטחת רשת."
                ),
                "Symantec (Broadcom)": (
                    "לאחר רכישת Broadcom, חדשנות אבטחת המידע של Symantec נעצרה. "
                    "Forcepoint מוביל עם ארכיטקטורת AI-native ופלטפורמת ענן מאוחדת מול הגישה המדורית של Symantec."
                ),
                "Microsoft Purview": (
                    "Purview מוגבל לאקוסיסטם M365. Forcepoint מאכף מדיניות עקבית "
                    "בכל הערוצים וספקים — הבחירה הנכונה לסביבות multi-cloud ו-multi-vendor."
                ),
            },
            objections_playbook=[
                {
                    "objection": "כבר יש לנו DLP — למה אנחנו צריכים את Forcepoint?",
                    "response": (
                        "DLP מדורי מאכף מדיניות ערוץ-ספציפית מבודדת עם false positives מופרזים. "
                        "Forcepoint מאחד DLP בכל הערוצים תחת מנוע מדיניות אחד מבוסס AI, "
                        "ומרחיב כיסוי לוקטורים מודרניים כמו GenAI שכלים ישנים אינם יכולים להגיע אליהם."
                    ),
                },
                {
                    "objection": "כבר משתמשים ב-Zscaler/Netskope — האם אנחנו צריכים פלטפורמה נוספת?",
                    "response": (
                        "Forcepoint הוא ה-SSE היחיד עם DLP בליבה באופן נטיבי — לא מוצמד בדיעבד. "
                        "לארגונים שבהם הגנת מידע היא העדיפות על פני שליטת גישה גרידא, "
                        "Forcepoint מספק כיסוי עמוק ומדויק יותר."
                    ),
                },
                {
                    "objection": "האם הפתרון מאושר FedRAMP?",
                    "response": (
                        "כן. Forcepoint ONE מחזיק אישור FedRAMP (NIST 800-53). "
                        "Forcepoint NGFW מאושר FIPS 140-3 Level 2, Common Criteria (NIAP) ונמצא ב-DoDIN APL. "
                        "ל-Forcepoint 20+ שנות ניסיון בשירות DoD, Intelligence Community וסוכנויות פדרליות."
                    ),
                },
                {
                    "objection": "כיצד מצדיקים את העלות?",
                    "response": (
                        "איחוד הפלטפורמה מבטל רישיונות מוצרים מרובים. "
                        "מחקר מוזמן מציג עד 31% חיסכון תפעולי, עם 91% שדיווחו על שיפור עמדת אבטחת המידע."
                    ),
                },
            ],
            discovery_questions=[
                "אילו אתגרי אבטחת מידע אתם מתמודדים איתם כיום בסביבות ענן, נקודות קצה ודואר אלקטרוני?",
                "כמה כלי אבטחה נפרדים אתם מנהלים להגנת מידע — והאם יש להם מדיניות מאוחדת?",
                "האם אתם מתמודדים עם דרישות ציות (GDPR, HIPAA, CMMC) ומתקשים בהיערכות לביקורות?",
                "האם הטמעתם בקרות כלשהן סביב שימוש עובדים באפליקציות GenAI כמו ChatGPT או Copilot?",
                "מהו הגישה הנוכחית שלכם לזיהוי ותגובה לאיומים פנימיים או דליפת מידע מקרית?",
            ],
            faq_kb_refs=[
                {
                    "q": "מהו Forcepoint ONE?",
                    "a": (
                        "Forcepoint ONE הוא פלטפורמת SSE ענן-native המשלבת SWG, CASB, ZTNA, RBI ו-DLP "
                        "לפלטפורמה אחת עם מנוע מדיניות מאוחד וקונסולת ניהול יחידה."
                    ),
                },
                {
                    "q": "האם Forcepoint תומך בסביבות BYOD?",
                    "a": (
                        "כן. Forcepoint ONE מספק תמיכה ללא-Agent למכשירי BYOD, "
                        "ומאכף מדיניות אבטחת מידע ובקרת גישה ללא צורך בסוכן מותקן."
                    ),
                },
                {
                    "q": "מהו Forcepoint DSPM וכיצד הוא שונה מ-DLP?",
                    "a": (
                        "DSPM מגלה ומעריך סיכוני מידע במנוחה באחסון ענן מרובה. "
                        "DLP מאכף בקרות מדיניות פעילות על מידע בתנועה בין ערוצים. "
                        "יחד הם מספקים הגנת מידע מלאה לאורך מחזור החיים."
                    ),
                },
                {
                    "q": "אילו תקני ציות Forcepoint תומך?",
                    "a": (
                        "GDPR, HIPAA, PCI-DSS, CMMC, NIST 800-53, NIST CSF 2.0, FISMA, NERC-CIP, "
                        "ISA/IEC 62443, ISO 27001, SOC 2, FIPS 140-3, FedRAMP, Common Criteria (NIAP), "
                        "DoDIN APL ועוד מאות עם תבניות מדיניות מובנות."
                    ),
                },
                {
                    "q": "כיצד Forcepoint שונה מ-DLP מדורי?",
                    "a": (
                        "DLP מדורי משתמש במדיניות-מבוססות-כללים סטטית עם שיעורי false positive גבוהים בערוצים מבודדים. "
                        "Forcepoint מאחד את כל הערוצים תחת מנוע AI Mesh אחד ומוסיף "
                        "Risk-Adaptive Protection — מתאים אכיפה בזמן אמת לפי התנהגות המשתמש."
                    ),
                },
            ],
            case_studies=[
                {
                    "title": "FBD Insurance — שיפור דיווח רגולטורי ושליטת מידע",
                    "industry": "שירותים פיננסיים / ביטוח",
                    "result": "שיפור שליטה על נתונים קריטיים עם דיווח רגולטורי משופר ותהליכי ציות יעילים יותר באמצעות Forcepoint DLP.",
                },
                {
                    "title": "Huber + Suhner — הגנה על פעילות גלובלית עם Forcepoint",
                    "industry": "ייצור",
                    "result": "השגת אמינות ואשכול לציות גלובלי, תוך ניווט בין דרישות אבטחת מידע בסמכויות שיפוט מרובות.",
                },
                {
                    "title": "Gartner Peer Insights Customers' Choice — SSE 2024",
                    "industry": "רב-סקטורי (65 לקוחות ארגוניים)",
                    "result": "ציון 98% המלצה; דירוג ממוצע 4.7/5.0 על פני 65 ביקורות לקוחות.",
                },
                {
                    "title": "איחוד אבטחת מידע מוביל ל-31% הפחתת עלויות תפעוליות",
                    "industry": "חוצה-תעשיות (מחקר מוזמן)",
                    "result": "עד 31% חיסכון תפעולי; 91% צופים שיפור בעמדת אבטחת המידע הכוללת.",
                },
            ],
            booking_link="https://www.forcepoint.com/contact-sales",
            cta_type="schedule_demo",
            handoff_rules={
                "triggers": [
                    "pricing", "contract", "security assessment", "competitor comparison",
                    "demo request", "talk to sales", "contact sales", "schedule a call",
                    "מחיר", "חוזה", "הדגמה", "דמו", "נציג", "מכירות",
                ],
                "target_queue": "sales-team",
                "user_msg_on_handoff": (
                    "אני מחבר אותך עם מומחה אבטחת Forcepoint "
                    "שייצור איתך קשר בקרוב לתיאום דמו מותאם אישית."
                ),
            },
            custom_prompt=(
                "גישת המכירה של Forcepoint היא ייעוצית ומתמקדת בארגונים. "
                "הובל לקוחות פוטנציאליים מתסכול של פיזור כלים או החלפת DLP מיושן "
                "לשיחה על פלטפורמת 'Data Security Everywhere' המאוחדת. "
                "צור דחיפות דרך סיכוני אימוץ GenAI, פיזור נתונים בענן, ולוחות זמנים של עמידה בתקנות. "
                "עגן הוכחה בהכרה מאנליסטים של Frost & Sullivan ו-Forrester, "
                "ציוני Gartner Peer Insights ועד 31% חיסכון תפעולי. "
                "כל CTA מוביל לדמו מותאם אישית."
            ),
        ))
        if inserted:
            print("✅ Forcepoint seeded successfully.")
        else:
            print("✅ Forcepoint record updated successfully.")
    except Exception as e:
        db.rollback()
        print(f"❌ Forcepoint seed failed: {e}")
        raise
    finally:
        db.close()


def seed_surf_club():
    """מועדון גלישה גאולה — B2C surf club demo company."""
    db = SessionLocal()
    try:
        inserted = _upsert_company(db, "geula-surf.co.il", dict(
            name="מועדון גלישה גאולה",
            domain="geula-surf.co.il",
            locale="he-IL",
            timezone="Asia/Jerusalem",
            currency="ILS",
            business_type="B2C",
            one_line_value="שיעורי גלישה מקצועיים על חוף תל אביב — לכל הרמות, מתחילים ועד מתקדמים.",
            products=[
                {
                    "id": "single_lesson",
                    "name": "שיעור גלישה יחיד",
                    "summary": "שיעור של 90 דקות עם מדריך מוסמך, כולל כל הציוד.",
                    "base_price": "₪280",
                    "details": "מדריך אישי לכל 2-3 תלמידים, ציוד כלול (גלשן + חליפה), מתחילים מתחילים בחוף הרדוד.",
                },
                {
                    "id": "package_5",
                    "name": "חבילת 5 שיעורים",
                    "summary": "חמישה שיעורים עם אותו מדריך לאורך כל הדרך.",
                    "base_price": "₪1,200",
                    "details": "חיסכון של ₪200 לעומת מחיר יחיד. תוקף 3 חודשים. הכי מומלץ למי שרוצה להתקדם.",
                },
                {
                    "id": "equipment_rental",
                    "name": "השכרת גלשן + חליפה",
                    "summary": "השכרת ציוד גלישה ליום שלם.",
                    "base_price": "₪120 ליום",
                    "details": "גלשנים בגדלים שונים, חליפות ניאופרן לכל המידות.",
                },
            ],
            pain_points=[
                "פחד מהגלים ולא יודעים מאיפה להתחיל",
                "ציוד גלישה יקר לרכישה",
                "חוסר ביטחון — האם אני מתאים לגלישה?",
                "לא יודע איזה מדריך לבחור",
            ],
            brand_voice={
                "style": "חברותי, אנרגטי, מעודד — כמו חבר שאוהב ים",
                "emoji_policy": "light",
                "closing_tone": "קביעת שיעור ראשון",
                "language": "עברית משוחררת, לא פורמלית",
                "avoid": "שאלות עסקיות כמו תפקיד, גודל חברה, תקציב שנתי",
            },
            icp=None,
            faq_kb_refs=[
                {"q": "האם אני צריך ניסיון?",
                 "a": "לא! רוב הלקוחות מגיעים ללא שום ניסיון. השיעורים שלנו מתחילים מאפס. "
                      "90% מהתלמידים עומדים על הגלשן כבר בשיעור הראשון."},
                {"q": "מה להביא לשיעור?",
                 "a": "רק בגד ים ומגבת — כל הציוד (גלשן + חליפה) כלול במחיר השיעור."},
                {"q": "האם זה מסוכן?",
                 "a": "הגלישה המלמדת מתבצעת בחוף רדוד ומוגן. כל השיעורים בפיקוח מדריך מוסמך. "
                      "הבטיחות היא עדיפות ראשונה."},
                {"q": "מה שעות הפעילות?",
                 "a": "ימים א'-ו', 07:00-18:00. שיעורים בתיאום מראש בלבד."},
            ],
            handoff_rules={
                "triggers": ["עורך דין", "תביעה", "נפצעתי", "תאונה"],
                "target_queue": "management",
                "user_msg_on_handoff": "אני מחבר אותך עם צוות הניהול שלנו.",
            },
            custom_fields={
                "fields": {
                    "surfing_level": "רמת גלישה (מתחיל/בינוני/מתקדם)",
                    "participants": "מספר משתתפים",
                    "preferred_date": "תאריך רצוי",
                    "goals": "מטרות (ללמוד/כיף/כושר)",
                }
            },
        ))
        if inserted:
            print("✅ מועדון גלישה גאולה seeded successfully.")
        else:
            print("גאולה surf club already seeded — skipping.")
    except Exception as e:
        db.rollback()
        print(f"❌ Surf club seed failed: {e}")
        raise
    finally:
        db.close()


def seed_scaleit():
    """SCALE IT — B2B IT consulting and automation demo company."""
    db = SessionLocal()
    try:
        inserted = _upsert_company(db, "scaleit.co.il", dict(
            name="SCALE IT",
            domain="scaleit.co.il",
            locale="he-IL",
            timezone="Asia/Jerusalem",
            currency="ILS",
            business_type="B2B",
            one_line_value="אוטומציה, CRM ודיגיטציה לעסקים בצמיחה — מ-0 ל-scale בלי לאבד לידים.",
            products=[
                {
                    "id": "free_assessment",
                    "name": "אבחון עסקי",
                    "summary": "פגישת אבחון חינמית של 60 דקות לזיהוי ה-bottlenecks בתהליכים.",
                    "base_price": "ללא עלות",
                    "details": "Zoom או פגישה פיזית. בסוף מקבלים מפת פעולה + ROI משוער.",
                },
                {
                    "id": "crm_automation",
                    "name": "יישום CRM + אוטומציה",
                    "summary": "יישום מלא של מערכת CRM + אוטומציה של תהליכי מכירות ו-follow-up.",
                    "base_price": "₪8,000 – ₪25,000",
                    "details": (
                        "עובדים עם HubSpot, Pipedrive, ו-Monday CRM. "
                        "כולל: pipeline מותאם, אינטגרציה עם WhatsApp/email, "
                        "אוטומציה של follow-up, דשבורד מכירות. "
                        "לקוחות מדווחים על 25-40% עלייה בסגירת עסקאות תוך 90 יום. "
                        "משך פרויקט: 4-8 שבועות."
                    ),
                },
                {
                    "id": "retainer",
                    "name": "ליווי שוטף — ריטיינר",
                    "summary": "שותף לצמיחה חודשי — תחזוקה, אוטומציות חדשות, ניתוח נתונים.",
                    "base_price": "₪3,500 לחודש",
                    "details": (
                        "כולל: review חודשי + action items, תחזוקת המערכות, "
                        "12-15 שעות עבודה חודשיות, זמינות לשאלות, "
                        "יישום שיפורים שוטפים."
                    ),
                },
            ],
            pain_points=[
                "תהליכים ידניים שאוכלים שעות עבודה בשבוע",
                "לידים שנופלים בין הכיסאות בגלל חוסר follow-up אוטומטי",
                "אין נראות על הנתונים — לא יודעים מה עובד",
                "מכירות שתלויות ב'זיכרון' של אנשי המכירות ולא במערכת",
                "שימוש ב-Excel/גיליון לניהול לקוחות",
            ],
            icp={
                "company_size": "5-50 עובדים",
                "industries": ["שירותים", "B2B", "אחסון ולוגיסטיקה", "טכנולוגיה", "יעוץ"],
                "buyer_roles": ["מנכ\"ל", "מנהל מכירות", "בעל עסק"],
                "growth_stage": "צמיחה מואצת — 500k-10M ₪ מחזור שנתי",
                "pain_trigger": "גדלים מהר מדי כדי לנהל ידנית",
            },
            brand_voice={
                "style": "מקצועי, יזמי, ישיר — סגנון יועץ אמיתי לא מוכר",
                "emoji_policy": "none",
                "closing_tone": "קביעת אבחון חינמי",
                "language": "עברית עסקית, בגובה העיניים",
                "avoid": "מינוח שיווקי מנופח, הבטחות מופרזות",
            },
            faq_kb_refs=[
                {"q": "כמה זמן לוקח יישום CRM?",
                 "a": "4-8 שבועות תלוי בגודל הארגון ומספר האינטגרציות. "
                      "שבוע 1: אבחון וסיכום דרישות. שבועות 2-6: יישום ובדיקות. שבוע 7-8: הדרכה ו-go live."},
                {"q": "איזה CRM אתם עובדים איתו?",
                 "a": "HubSpot למי שמחפש פלטפורמה מלאה + marketing. "
                      "Pipedrive למי שמוכר-מוכר ורוצה simplicity. "
                      "Monday CRM למי שכבר עובד עם Monday. "
                      "אנחנו בוחרים ביחד לפי הצרכים שלך."},
                {"q": "האם יש אחריות על התוצאות?",
                 "a": "אנחנו לא מבטיחים מספרים — אבל לקוחות שלנו מדווחים בממוצע על "
                      "25-40% שיפור בסגירת עסקאות ו-12-15 שעות חיסכון שבועי."},
            ],
            handoff_rules={
                "triggers": ["הצעת מחיר", "חוזה", "עורך דין", "שאלה משפטית"],
                "target_queue": "sales-team",
                "user_msg_on_handoff": "אני מחבר אותך עם מנהל המכירות שלנו לתיאום פגישה.",
            },
            differentiators=[
                "לא מוכרים תוכנה — מלווים את כל תהליך היישום",
                "ROI מוכח — מחשבים את ה-break-even יחד לפני שמתחילים",
                "ניסיון עם 50+ עסקים בצמיחה בישראל",
                "אין lock-in — הכל שלך אחרי הפרויקט",
            ],
        ))
        if inserted:
            print("✅ SCALE IT seeded successfully.")
        else:
            print("SCALE IT already seeded — skipping.")
    except Exception as e:
        db.rollback()
        print(f"❌ SCALE IT seed failed: {e}")
        raise
    finally:
        db.close()


def seed_all():
    """Run all seed functions."""
    seed_demo_company()
    seed_surf_club()
    seed_scaleit()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Seeding demo data...")
    seed_all()
    print("Done!")

