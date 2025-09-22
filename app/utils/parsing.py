import csv, json, io
from ..extensions import db
from ..models import Question

ALLOWED_EXT = {'txt', 'json', 'csv'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def normalize_option(label: str, text: str) -> str:
    text = (text or '').strip()
    prefix = f"{label}. "
    return text if text.startswith(prefix) else f"{prefix}{text}"

def save_questions(rows, subject_id: int):
    for r in rows:
        q = Question(
            subject_id=subject_id,
            content=r['content'].strip(),
            option_a=normalize_option('A', r['option_a']),
            option_b=normalize_option('B', r['option_b']),
            option_c=normalize_option('C', r['option_c']),
            option_d=normalize_option('D', r['option_d']),
            correct_answer=r['correct_answer'].upper().strip()
        )
        db.session.add(q)
    db.session.commit()

def parse_uploaded_file(file_storage):
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    rows = []
    data = file_storage.read().decode('utf-8')
    if ext == 'json':
        arr = json.loads(data)
        for it in arr:
            rows.append({
                'content': it.get('content',''),
                'option_a': it.get('option_a',''),
                'option_b': it.get('option_b',''),
                'option_c': it.get('option_c',''),
                'option_d': it.get('option_d',''),
                'correct_answer': it.get('correct_answer','')
            })
    elif ext == 'csv':
        reader = csv.DictReader(io.StringIO(data))
        for r in reader:
            rows.append({
                'content': r.get('content',''),
                'option_a': r.get('option_a',''),
                'option_b': r.get('option_b',''),
                'option_c': r.get('option_c',''),
                'option_d': r.get('option_d',''),
                'correct_answer': r.get('correct_answer','')
            })
    else:  # txt pipe-delimited: content|A|B|C|D|answer
        for ln, line in enumerate(io.StringIO(data), 1):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) == 6:
                rows.append({
                    'content': parts[0],
                    'option_a': parts[1],
                    'option_b': parts[2],
                    'option_c': parts[3],
                    'option_d': parts[4],
                    'correct_answer': parts[5]
                })
    return [r for r in rows if r['content'] and r['correct_answer'].upper() in {'A','B','C','D'}]
