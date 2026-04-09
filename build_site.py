import os
import json
import time
import argparse
from jinja2 import Environment, FileSystemLoader


def normalize_level(raw_level, default_level="intermediate"):
    level = str(raw_level or default_level).strip().lower()
    allowed = {"beginner", "intermediate", "advanced"}
    return level if level in allowed else default_level


def level_label(level):
    labels = {
        "beginner": "Beginner",
        "intermediate": "Intermediate",
        "advanced": "Advanced",
    }
    return labels.get(level, "Intermediate")


def platform_slug(platform):
    normalized = str(platform or "web").strip().lower()
    for char in [" ", "/", "_", "."]:
        normalized = normalized.replace(char, "-")
    return normalized or "web"

def load_data(file_path="data.json"):
    if not os.path.exists(file_path):
        print(f"❌ שגיאה: הקובץ {file_path} לא נמצא!")
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ שגיאה בקריאת ה-JSON: {e}")
        return None

def add_csv_data(csv_file, data_file="data.json"):
    """Add new data from CSV file to existing data.json"""
    import csv
    
    data = load_data(data_file)
    if not data:
        return False
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                section = row.get('section', '').strip()
                item_type = row.get('type', '').strip()  # 'guide' or 'tool'
                subject_name = row.get('subject', '').strip()
                
                if section in data and item_type in ['guide', 'tool']:
                    item = {
                        'title': row.get('title', '').strip(),
                        'desc': row.get('description', '').strip(),
                        'url': row.get('url', '').strip()
                    }
                    # Add optional fields if present
                    if 'difficulty' in row:
                        item['difficulty'] = row['difficulty'].strip()
                    if 'duration' in row:
                        item['duration'] = row['duration'].strip()
                    if 'tags' in row:
                        item['tags'] = [tag.strip() for tag in row['tags'].split(',')]

                    if item_type == 'guide':
                        if subject_name and isinstance(data[section].get('subjects'), list):
                            subject = next((s for s in data[section]['subjects'] if s.get('title') == subject_name), None)
                            if subject is None:
                                subject = {'title': subject_name, 'guides': []}
                                data[section]['subjects'].append(subject)
                            subject.setdefault('guides', []).append(item)
                        else:
                            data[section].setdefault('guides', []).append(item)
                    else:
                        data[section].setdefault('tools', []).append(item)
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ נתונים מ-{csv_file} נוספו בהצלחה ל-{data_file}")
        return True
    except Exception as e:
        print(f"❌ שגיאה בהוספת נתונים מ-CSV: {e}")
        return False

def add_json_data(json_file, data_file="data.json"):
    """Add new data from JSON file to existing data.json"""
    data = load_data(data_file)
    if not data:
        return False
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            new_data = json.load(f)
        
        # Merge new data into existing data
        for section, content in new_data.items():
            if section in data:
                # Merge guides and tools
                if 'guides' in content:
                    data[section].setdefault('guides', []).extend(content['guides'])
                if 'subjects' in content:
                    data[section].setdefault('subjects', []).extend(content['subjects'])
                if 'tools' in content:
                    data[section].setdefault('tools', []).extend(content['tools'])
                # Update other fields if provided
                for key, value in content.items():
                    if key not in ['guides', 'subjects', 'tools']:
                        data[section][key] = value
            else:
                # Add new section
                data[section] = content
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ נתונים מ-{json_file} נוספו בהצלחה ל-{data_file}")
        return True
    except Exception as e:
        print(f"❌ שגיאה בהוספת נתונים מ-JSON: {e}")
        return False

def generate_ultimate_portal(data, output_file="index.html"):
    if not data:
        return

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('base.html')

    nav_html = ""
    sections_html = ""
    creators_panel_html = ""

    creators_data = data.get("creators", {})
    creators_items = creators_data.get("creators", []) if isinstance(creators_data, dict) else []
    if creators_items:
        creators_cards_html = ""
        for c in creators_items:
            platform = c.get("platform", "Web")
            platform_class = platform_slug(platform)
            creators_cards_html += f'''
            <a href="{c.get('url', '#')}" target="_blank" class="creator-panel-card">
                <div class="creator-panel-head">
                    <span class="creator-name">{c.get('name', '')}</span>
                    <span class="creator-platform-badge platform-{platform_class}">{platform}</span>
                </div>
                <p class="creator-desc">{c.get('desc', '')}</p>
                <span class="creator-link">בקרו בערוץ →</span>
            </a>'''

        creators_panel_html = f'''
        <button type="button" class="floating-creators-btn" onclick="toggleCreatorsPanel()" aria-controls="creatorsPanel" aria-expanded="false">
            ⭐ יוצרים מומלצים
        </button>
        <div id="creatorsBackdrop" class="creators-backdrop" onclick="closeCreatorsPanel()"></div>
        <aside id="creatorsPanel" class="creators-panel" aria-hidden="true">
            <div class="creators-panel-header">
                <h3>{creators_data.get('title', 'יוצרים מומלצים')}</h3>
                <button type="button" class="creators-close" onclick="closeCreatorsPanel()" aria-label="סגור">×</button>
            </div>
            <p class="creators-panel-subtitle">{creators_data.get('description', '')}</p>
            <div class="creators-panel-list">{creators_cards_html}</div>
        </aside>'''
    
    # מעבר על כל הקטגוריות ב-JSON
    visible_index = 0
    for key, val in data.items():
        if key.lower() == "creators":
            continue

        # הקטגוריה הראשונה ב-JSON תהיה הפעילה (Active) כברירת מחדל
        active_class = "active" if visible_index == 0 else ""
        visible_index += 1
        
        # 1. בניית פריט בתפריט הניווט
        nav_html += f'''
        <div class="nav-item {active_class}" onclick="showSection('{key}', this)">
            <span class="nav-icon">{val.get('emoji', '🚀')}</span>
            <span class="nav-text">{val.get('title', 'ללא כותרת')}</span>
        </div>'''
        
        # 2. בניית תוכן הסקשן
        if key.lower() == "home":
            # עיצוב מיוחד לדף הבית
            content_body = f'''
            <div class="welcome-container">
                <div class="welcome-card">
                    <h1>AI Roadmap: המסלול שאני בעצמי רציתי שיהיה לי 🚀</h1>
                    <p>בניתי את הדף הזה אחרי לא מעט בלגן של קישורים, סרטונים ומאמרים שנשמרו בכל מקום אפשרי. רציתי סוף סוף לרכז הכל במקום אחד, מסודר ונעים, כדי שאני וגם חברים שלי נוכל ללמוד בלי ללכת לאיבוד.</p>
                    <p>מה שתמצאו כאן זה לא "קורס רשמי", אלא אוסף אישי של תכנים שבאמת עזרו לי להבין את התחום צעד אחרי צעד. אם זה יעזור גם לכם להתקדם קצת יותר מהר, עשיתי את שלי.</p>
                    
                    <div class="contact-links">
                        <p><strong>בואו נשתמע:</strong></p>
                        <div class="contact-links-row">
                            <a href="https://www.linkedin.com/in/noamiman/" target="_blank" class="contact-link-card">
                                <span class="contact-link-icon">in</span>
                                <span class="contact-link-text">
                                    <span class="contact-link-title">LinkedIn</span>
                                    <span class="contact-link-subtitle">תתחברו אליי</span>
                                </span>
                            </a>
                            <a href="https://github.com/noamiman" target="_blank" class="contact-link-card">
                                <span class="contact-link-icon">&lt;/&gt;</span>
                                <span class="contact-link-text">
                                    <span class="contact-link-title">GitHub</span>
                                    <span class="contact-link-subtitle">לפרויקטים שלי</span>
                                </span>
                            </a>
                        </div>
                    </div>

                    <div class="welcome-footer">
                        <p>💡 <strong>איך להשתמש באתר?</strong> בחרו נושא מהתפריט בצד והתחילו ללמוד!</p>
                    </div>
                </div>
            </div>'''
        else:
            # עיצוב רגיל למסלול למידה (Roadmap)
            guides_html = ""
            subjects = val.get("subjects", [])

            if subjects:
                idx = 1
                for subject in subjects:
                    subject_level = normalize_level(subject.get("level"), val.get("difficulty", "intermediate"))
                    subject_level_label = level_label(subject_level)
                    subject_guides_html = ""
                    for g in subject.get("guides", []):
                        g_url = g.get('url', '#')
                        g_id = g_url.replace('"', '')
                        subject_guides_html += f'''
                        <div class="step-item">
                            <div class="step-marker">{idx}</div>
                            <div class="step-card-wrapper" data-url="{g_id}">
                                <a href="{g_url}" target="_blank" class="step-card">
                                    <h4>{g.get('title', 'מדריך ללא שם')}</h4>
                                    <p>{g.get('desc', '')}</p>
                                    <span class="step-link">צפה במדריך ←</span>
                                </a>
                                <button type="button" class="seen-btn" onclick="toggleSeen(this)" aria-label="סמן כנצפה" title="סמן כנצפה">✓</button>
                            </div>
                        </div>'''
                        idx += 1

                    if not subject_guides_html:
                        subject_guides_html = '<p class="subject-empty">אין עדיין קישורים בנושא זה.</p>'

                    guides_html += f'''
                    <div class="subject-group level-{subject_level}">
                        <h4 class="subject-title">
                            <span>{subject.get('title', 'נושא')}</span>
                            <span class="subject-level-badge">{subject_level_label}</span>
                        </h4>
                        <div class="subject-items">{subject_guides_html}</div>
                    </div>'''
            else:
                for idx, g in enumerate(val.get("guides", []), 1):
                    g_url = g.get('url', '#')
                    g_id = g_url.replace('"', '')
                    guides_html += f'''
                    <div class="step-item">
                        <div class="step-marker">{idx}</div>
                        <div class="step-card-wrapper" data-url="{g_id}">
                            <a href="{g_url}" target="_blank" class="step-card">
                                <h4>{g.get('title', 'מדריך ללא שם')}</h4>
                                <p>{g.get('desc', '')}</p>
                                <span class="step-link">צפה במדריך ←</span>
                            </a>
                            <button type="button" class="seen-btn" onclick="toggleSeen(this)" aria-label="סמן כנצפה" title="סמן כנצפה">✓</button>
                        </div>
                    </div>'''

            tools_html = ""
            for t in val.get("tools", []):
                tools_html += f'''
                <div class="tool-card">
                    <div class="tool-info">
                        <h5>{t.get('title', 'כלי')}</h5>
                        <p>{t.get('desc', '')}</p>
                    </div>
                    <a href="{t.get('url', '#')}" target="_blank" class="tool-btn">פתח כלי</a>
                </div>'''
            
            content_body = f'''
            <div class="section-header">
                <span class="badge">מסלול למידה</span>
                <h2><span class="emoji">{val.get('emoji', '')}</span> {val.get('title', '')}</h2>
                <p>{val.get('description', '')}</p>
            </div>
            <div class="main-layout">
                <div class="roadmap-box">
                    <h3 class="box-title">🗺️ שלבי הלמידה</h3>
                    <div class="roadmap-timeline">{guides_html}</div>
                </div>
                <div class="tools-box">
                    <h3 class="box-title">🛠️ כלים שימושיים</h3>
                    <div class="tools-list">{tools_html}</div>
                </div>
            </div>'''

        # הוספת הסקשן ל-HTML הכללי
        sections_html += f'''
        <section id="{key}" class="content-section {active_class}">
            {content_body}
        </section>'''

    # Render the template with Jinja2
    html_content = template.render(
        nav_html=nav_html,
        sections_html=sections_html,
        creators_panel_html=creators_panel_html,
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"🔥 האתר נוצר בכתובת: {os.path.abspath(output_file)}")


def build_once(data_file="data.json", output_file="index.html"):
    data = load_data(data_file)
    if data:
        generate_ultimate_portal(data, output_file=output_file)
        return True
    return False


def watch_and_build(data_file="data.json", output_file="index.html", interval=1.0):
    watched_files = [
        data_file,
        "templates/base.html",
        __file__,
    ]

    mtimes = {}
    for path in watched_files:
        if os.path.exists(path):
            mtimes[path] = os.path.getmtime(path)

    print("👀 מצב מעקב פעיל - נשמר שינוי? האתר ייבנה אוטומטית")
    print("🛑 לעצירה: Ctrl+C")

    build_once(data_file=data_file, output_file=output_file)

    while True:
        try:
            changed = False
            for path in watched_files:
                if not os.path.exists(path):
                    continue

                current_mtime = os.path.getmtime(path)
                if mtimes.get(path) != current_mtime:
                    mtimes[path] = current_mtime
                    changed = True

            if changed:
                print("\n🔁 זוהה שינוי בקבצים, בונה מחדש...")
                build_once(data_file=data_file, output_file=output_file)

            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n✅ מצב מעקב הופסק")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build AI roadmap site")
    parser.add_argument("--watch", action="store_true", help="Automatically rebuild when files change")
    parser.add_argument("--interval", type=float, default=1.0, help="Watch polling interval in seconds")
    parser.add_argument("--data", default="data.json", help="Path to data JSON file")
    parser.add_argument("--output", default="index.html", help="Output HTML path")
    args = parser.parse_args()

    if args.watch:
        watch_and_build(data_file=args.data, output_file=args.output, interval=args.interval)
    else:
        build_once(data_file=args.data, output_file=args.output)