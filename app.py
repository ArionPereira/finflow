from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

DB_PATH = os.environ.get('DB_PATH', os.path.join(
    '/data' if os.path.exists('/data') else os.path.dirname(__file__),
    'finance.db'
))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('receita','despesa')),
        color TEXT DEFAULT '#6366f1',
        icon TEXT DEFAULT '💰',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('receita','despesa')),
        category_id INTEGER REFERENCES categories(id),
        date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0,
        deadline TEXT,
        color TEXT DEFAULT '#10b981',
        icon TEXT DEFAULT '🎯',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('SELECT COUNT(*) FROM categories')
    if c.fetchone()[0] == 0:
        defaults = [
            ('Salário','receita','#10b981','💼'),('Freelance','receita','#06b6d4','💻'),
            ('Investimentos','receita','#f59e0b','📈'),('Outros (Receita)','receita','#8b5cf6','💰'),
            ('Alimentação','despesa','#ef4444','🍔'),('Moradia','despesa','#f97316','🏠'),
            ('Transporte','despesa','#eab308','🚗'),('Saúde','despesa','#ec4899','❤️'),
            ('Lazer','despesa','#8b5cf6','🎮'),('Educação','despesa','#06b6d4','📚'),
            ('Roupas','despesa','#f59e0b','👕'),('Outros (Despesa)','despesa','#6b7280','📦'),
        ]
        c.executemany('INSERT INTO categories (name,type,color,icon) VALUES (?,?,?,?)', defaults)
    conn.commit()
    conn.close()

# ---- SERVE PWA FILES ----
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def service_worker():
    return send_from_directory('.', 'sw.js')

@app.route('/icon-192.png')
def icon192():
    return send_from_directory('.', 'icon-192.png')

@app.route('/icon-512.png')
def icon512():
    return send_from_directory('.', 'icon-512.png')

# ---- TRANSACTIONS ----
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    month = request.args.get('month')
    year = request.args.get('year')
    conn = get_db()
    query = '''SELECT t.*, c.name as category_name, c.color as category_color, c.icon as category_icon
               FROM transactions t LEFT JOIN categories c ON t.category_id = c.id'''
    params = []
    if month:
        query += ' WHERE t.date LIKE ?'; params.append(f'{month}%')
    elif year:
        query += ' WHERE t.date LIKE ?'; params.append(f'{year}%')
    query += ' ORDER BY t.date DESC, t.created_at DESC'
    rows = [dict(r) for r in conn.execute(query, params).fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO transactions (description,amount,type,category_id,date,notes) VALUES (?,?,?,?,?,?)',
              (data['description'],float(data['amount']),data['type'],data.get('category_id'),data['date'],data.get('notes','')))
    conn.commit(); tid = c.lastrowid; conn.close()
    return jsonify({'id': tid}), 201

@app.route('/api/transactions/<int:tid>', methods=['PUT'])
def update_transaction(tid):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE transactions SET description=?,amount=?,type=?,category_id=?,date=?,notes=? WHERE id=?',
                 (data['description'],float(data['amount']),data['type'],data.get('category_id'),data['date'],data.get('notes',''),tid))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

@app.route('/api/transactions/<int:tid>', methods=['DELETE'])
def delete_transaction(tid):
    conn = get_db()
    conn.execute('DELETE FROM transactions WHERE id=?', (tid,))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

# ---- CATEGORIES ----
@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db()
    rows = [dict(r) for r in conn.execute('SELECT * FROM categories ORDER BY type,name').fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    conn = get_db(); c = conn.cursor()
    c.execute('INSERT INTO categories (name,type,color,icon) VALUES (?,?,?,?)',
              (data['name'],data['type'],data.get('color','#6366f1'),data.get('icon','💰')))
    conn.commit(); cid = c.lastrowid; conn.close()
    return jsonify({'id': cid}), 201

@app.route('/api/categories/<int:cid>', methods=['DELETE'])
def delete_category(cid):
    conn = get_db()
    conn.execute('DELETE FROM categories WHERE id=?', (cid,))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

# ---- GOALS ----
@app.route('/api/goals', methods=['GET'])
def get_goals():
    conn = get_db()
    rows = [dict(r) for r in conn.execute('SELECT * FROM goals ORDER BY created_at DESC').fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/goals', methods=['POST'])
def create_goal():
    data = request.json
    conn = get_db(); c = conn.cursor()
    c.execute('INSERT INTO goals (name,target_amount,current_amount,deadline,color,icon) VALUES (?,?,?,?,?,?)',
              (data['name'],float(data['target_amount']),float(data.get('current_amount',0)),data.get('deadline'),data.get('color','#10b981'),data.get('icon','🎯')))
    conn.commit(); gid = c.lastrowid; conn.close()
    return jsonify({'id': gid}), 201

@app.route('/api/goals/<int:gid>', methods=['PUT'])
def update_goal(gid):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE goals SET name=?,target_amount=?,current_amount=?,deadline=?,color=?,icon=? WHERE id=?',
                 (data['name'],float(data['target_amount']),float(data.get('current_amount',0)),data.get('deadline'),data.get('color','#10b981'),data.get('icon','🎯'),gid))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

@app.route('/api/goals/<int:gid>', methods=['DELETE'])
def delete_goal(gid):
    conn = get_db()
    conn.execute('DELETE FROM goals WHERE id=?', (gid,))
    conn.commit(); conn.close()
    return jsonify({'ok': True})

# ---- SUMMARY ----
@app.route('/api/summary', methods=['GET'])
def get_summary():
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='receita' AND date LIKE ?", (f'{month}%',))
    receitas = c.fetchone()[0]
    c.execute("SELECT COALESCE(SUM(amount),0) FROM transactions WHERE type='despesa' AND date LIKE ?", (f'{month}%',))
    despesas = c.fetchone()[0]
    c.execute('''SELECT c.name,c.color,c.icon,SUM(t.amount) as total
                 FROM transactions t JOIN categories c ON t.category_id=c.id
                 WHERE t.type='despesa' AND t.date LIKE ? GROUP BY c.id ORDER BY total DESC LIMIT 8''', (f'{month}%',))
    despesas_cat = [dict(r) for r in c.fetchall()]
    c.execute('''SELECT strftime('%Y-%m',date) as month,
                        SUM(CASE WHEN type='receita' THEN amount ELSE 0 END) as receitas,
                        SUM(CASE WHEN type='despesa' THEN amount ELSE 0 END) as despesas
                 FROM transactions GROUP BY month ORDER BY month DESC LIMIT 6''')
    trend = list(reversed([dict(r) for r in c.fetchall()]))
    conn.close()
    return jsonify({'receitas':receitas,'despesas':despesas,'saldo':receitas-despesas,'despesas_por_categoria':despesas_cat,'trend':trend})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
