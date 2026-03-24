import json
import re

def extract_date_score(date_str):
    if not date_str:
        return 999912
    
    years = re.findall(r'\b(20\d\d)\b', str(date_str))
    year_val = int(years[0]) if years else 1970
    
    months_map = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2,
        'mar': 3, 'march': 3, 'apr': 4, 'april': 4,
        'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'september': 9,
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    found_month = 1
    words = re.findall(r'[a-zA-Z]+', str(date_str))
    for word in words:
        wl = word.lower()
        if wl in months_map:
            found_month = months_map[wl]
            break
    
    return (year_val * 100) + found_month

try:
    with open('data/portfolio.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    print("Loaded DB. Total projects:", len(db['projects']))
    
    for idx, p in enumerate(db['projects']):
        try:
            score = extract_date_score(p.get('date', ''))
            print(f"Project {idx}: date='{p.get('date', '')}' -> {score}")
        except Exception as inner_e:
            print(f"Failed at project {idx}: {p}, Error: {inner_e}")
            raise inner_e

    db['projects'].sort(key=lambda x: extract_date_score(x.get('date', '')), reverse=True)
    print("Sorted successfully.")

except Exception as e:
    print("Error:", e)
