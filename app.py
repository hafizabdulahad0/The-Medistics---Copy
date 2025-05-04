import pandas as pd
import openai
from datetime import date, datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash
)
from functools import wraps
import database  # your database.py

app = Flask(__name__)
app.secret_key = 'dev_secret_key'  # change in production!

# Path to your Excel question bank
EXCEL_FILE = 'questions.xlsx'

# Supported subjects
ALL_SUBJECTS = ["Biology", "Chemistry", "Physics", "English", "Logical Reasoning"]

# Initialize (and create) tables
database.init_db()

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapped

@app.route('/')
def main_landing():
    return render_template('main.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        fullname = request.form.get('fullname','').strip()
        email    = request.form.get('usermail','').strip()
        pwd      = request.form.get('user','')
        if not fullname or not email or not pwd:
            return render_template('signup.html', error="All fields are required.")
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            conn.close()
            return render_template('signup.html', error="Email already registered.")
        conn.close()
        session['pending_fullname'] = fullname
        session['pending_email']    = email
        session['pending_password'] = pwd
        return redirect(url_for('choose_username'))
    return render_template('signup.html')

@app.route('/choose_username', methods=['GET','POST'])
def choose_username():
    if 'pending_email' not in session:
        return redirect(url_for('signup'))
    if request.method=='POST':
        username = request.form.get('username','').strip()
        if not username:
            return render_template('chooseusername.html', error_type="empty")
        import re
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return render_template('chooseusername.html', error_type="invalid")
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone():
            conn.close()
            return render_template('chooseusername.html', error_type="taken")
        conn.close()
        session['pending_username'] = username
        return redirect(url_for('userinfo'))
    return render_template('chooseusername.html')

@app.route('/userinfo', methods=['GET','POST'])
def userinfo():
    if 'pending_username' not in session:
        return redirect(url_for('signup'))
    if request.method=='POST':
        province = request.form.get('province')
        if not province:
            flash("Please select a province.")
            return render_template('userinfo.html')
        session['pending_province'] = province
        return redirect(url_for('userinfo2'))
    return render_template('userinfo.html')

@app.route('/userinfo2', methods=['GET','POST'])
def userinfo2():
    if 'pending_province' not in session:
        return redirect(url_for('signup'))
    if request.method=='POST':
        heard = request.form.get('heared')
        if not heard:
            flash("Please select how you heard about us.")
            return render_template('userinfo2.html')
        session['pending_referral'] = heard
        return redirect(url_for('userinfo3'))
    return render_template('userinfo2.html')

@app.route('/userinfo3', methods=['GET','POST'])
def userinfo3():
    if 'pending_referral' not in session:
        return redirect(url_for('signup'))
    if request.method=='POST':
        theme = request.form.get('dlmode','Light')
        # gather pending data
        full = session.pop('pending_fullname')
        email= session.pop('pending_email')
        pwd  = session.pop('pending_password')
        user = session.pop('pending_username')
        prov = session.pop('pending_province')
        ref  = session.pop('pending_referral')
        dt   = date.today().isoformat()
        plan = 'Basic'
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("""
          INSERT INTO users
            (full_name,email,password,username,province,referral_source,theme,subscription_plan,signup_date)
          VALUES (?,?,?,?,?,?,?,?,?)
        """, (full,email,pwd,user,prov,ref,theme,plan,dt))
        conn.commit()
        uid = cur.lastrowid
        conn.close()
        session.clear()
        session['user_id']  = uid
        session['username'] = user
        return redirect(url_for('index'))
    return render_template('userinfo3.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
    if request.method=='POST':
        uid = request.form.get('userid','').strip()
        pwd = request.form.get('user','')
        if not uid or not pwd:
            return render_template('login.html', error="Enter both fields.")
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT id,username,password FROM users WHERE username=? OR email=?", (uid,uid))
        row = cur.fetchone()
        conn.close()
        if not row or row['password'] != pwd:
            return render_template('login.html', error="Invalid credentials.")
        session.clear()
        session['user_id']  = row['id']
        session['username'] = row['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
@login_required
def index():
    uid = session['user_id']
    conn = database.get_db_connection()
    cur  = conn.cursor()
    cur.execute("""
        SELECT bio_correct, bio_total,
               chem_correct, chem_total,
               phy_correct, phy_total,
               eng_correct, eng_total,
               lr_correct,  lr_total
        FROM users WHERE id = ?
    """, (uid,))
    u = cur.fetchone()
    conn.close()

    parts = [
        (u['bio_correct'], u['bio_total']),
        (u['chem_correct'], u['chem_total']),
        (u['phy_correct'], u['phy_total']),
        (u['eng_correct'], u['eng_total']),
        (u['lr_correct'],  u['lr_total'])
    ]
    total_correct = sum(c for c, t in parts)
    total_qs      = sum(t for c, t in parts)
    career_score  = int((total_correct / total_qs)*100) if total_qs else 0

    return render_template(
        'index.html',
        t_correct=total_correct,
        t_total=total_qs,
        career_score=career_score
    )

@app.route('/account')
@login_required
def account():
    uid = session['user_id']
    conn = database.get_db_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (uid,))
    user = cur.fetchone()
    conn.close()

    def pct(c,t): return int(c/t*100) if t else 0
    bio_p  = pct(user['bio_correct'], user['bio_total'])
    chem_p = pct(user['chem_correct'], user['chem_total'])
    phy_p  = pct(user['phy_correct'], user['phy_total'])
    eng_p  = pct(user['eng_correct'], user['eng_total'])
    lr_p   = pct(user['lr_correct'],  user['lr_total'])
    total_corr = (
        user['bio_correct'] + user['chem_correct'] +
        user['phy_correct'] + user['eng_correct'] +
        user['lr_correct']
    )
    total_q    = (
        user['bio_total'] + user['chem_total'] +
        user['phy_total'] + user['eng_total'] +
        user['lr_total']
    )
    total_pct = pct(total_corr, total_q)

    return render_template(
        'account.html',
        user=user,
        bio_percent=bio_p,
        chem_percent=chem_p,
        phy_percent=phy_p,
        eng_percent=eng_p,
        lr_percent=lr_p,
        total_percent=total_pct,
        total_correct=total_corr,
        total_qs=total_q
    )

@app.route('/accsettings', methods=['GET','POST'])
@login_required
def accsettings():
    uid = session['user_id']
    conn = database.get_db_connection()
    cur  = conn.cursor()
    if request.method=='POST':
        api_key = request.form.get('api_key','').strip()
        cur.execute("UPDATE users SET openai_api_key=? WHERE id=?", (api_key, uid))
        conn.commit()
        flash("API key updated.")
    cur.execute("SELECT * FROM users WHERE id=?", (uid,))
    user = cur.fetchone()
    cur.execute(
        "SELECT plan, amount, method, payment_date, status "
        "FROM payments WHERE user_id=? ORDER BY id",
        (uid,)
    )
    payments = cur.fetchall()
    conn.close()

    signup_dt = datetime.strptime(user['signup_date'], "%Y-%m-%d").date()
    days_used = (date.today() - signup_dt).days

    return render_template(
        'accsettings.html',
        user=user,
        payments=payments,
        days=days_used
    )

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/subscribe', methods=['POST'])
@login_required
def subscribe():
    plan_choice = request.form.get('card','').lower()
    mapping = {
        'basic':   ('Basic',   0),
        'standart':('Gold',   150),
        'premium': ('Iconic', 300)
    }
    if plan_choice not in mapping:
        flash("Invalid plan.")
        return redirect(url_for('pricing'))
    plan_name, amount = mapping[plan_choice]
    uid = session['user_id']
    conn = database.get_db_connection()
    cur  = conn.cursor()
    cur.execute("UPDATE users SET subscription_plan=? WHERE id=?", (plan_name, uid))
    if plan_name!='Basic':
        pay_date = date.today().isoformat()
        cur.execute(
            "INSERT INTO payments (user_id,plan,amount,method,payment_date,status) "
            "VALUES (?,?,?,?,?,?)",
            (uid, plan_name, amount, "Online", pay_date, "Confirmed")
        )
    conn.commit()
    conn.close()
    flash(f"Subscribed to {plan_name}.")
    return redirect(url_for('accsettings'))

@app.route('/testsettings', methods=['GET','POST'])
@login_required
def testsettings():
    if request.method=='POST':
        subjects = request.form.getlist('subjects')
        num_q    = int(request.form.get('num_questions','0'))
        if 'All' in subjects:
            subjects = ALL_SUBJECTS.copy()
        if not subjects or num_q <= 0:
            flash("Select subjects and number of questions.")
            return redirect(url_for('testsettings'))

        # fetch user plan & API key
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT subscription_plan, openai_api_key FROM users WHERE id=?", (session['user_id'],))
        uinfo = cur.fetchone()
        conn.close()

        use_ai = (uinfo['subscription_plan']=='Iconic' and uinfo['openai_api_key'])
        questions_list = []

        # AI-based generation for Iconic users
        if use_ai:
            openai.api_key = uinfo['openai_api_key']
            for _ in range(num_q):
                try:
                    res = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role":"system","content":"You are an expert MDCAT tutor."},
                            {"role":"user","content":
                                f"Generate a JSON MCQ for subjects {', '.join(subjects)} "
                                "including question, options[], answer, explanation."}
                        ],
                        temperature=0.7
                    )
                    import json, re
                    msg = res.choices[0].message.content
                    js  = re.search(r'\{.*\}', msg, re.DOTALL).group()
                    data= json.loads(js)
                    opts= data['options']
                    ans = data['answer']
                    idx = None
                    if isinstance(ans, int):
                        idx = ans
                    else:
                        if ans in opts:
                            idx = opts.index(ans)+1
                        elif ans.lower() in ['a','b','c','d']:
                            idx = ['a','b','c','d'].index(ans.lower())+1
                    if not (1<=idx<=4):
                        continue
                    questions_list.append({
                        'id': f"AI{len(questions_list)}",
                        'subject': "/".join(subjects),
                        'question_text': data['question'],
                        'options': opts,
                        'correct_option': idx,
                        'explanation': data['explanation']
                    })
                except:
                    continue
            if not questions_list:
                use_ai = False

        # Fallback: pull from Excel for Basic/Gold or AI failures
        if not use_ai:
            df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
            df = df[df['subject'].isin(subjects)]
            if len(df) < num_q:
                num_q = len(df)
            sampled = df.sample(n=num_q) if num_q>0 else df
            for idx, row in sampled.iterrows():
                questions_list.append({
                    'id': f"X{idx}",
                    'subject': row['subject'],
                    'question_text': row['question_text'],
                    'options': [
                        row['option1'], row['option2'],
                        row['option3'], row['option4']
                    ],
                    'correct_option': int(row['correct_option']),
                    'explanation': row['explanation']
                })

        session['questions']     = questions_list
        session['current_q_idx'] = 0
        session['total_qs']      = len(questions_list)
        return redirect(url_for('test'))

    return render_template('testsettings.html')

@app.route('/test', methods=['GET','POST'])
@login_required
def test():
    if 'questions' not in session:
        return redirect(url_for('testsettings'))
    qs    = session['questions']
    idx   = session['current_q_idx']
    total = session['total_qs']
    if request.method=='POST':
        choice = request.form.get('options')
        q      = qs[idx]
        corr   = q['correct_option']
        is_corr = (int(choice)==corr) if choice else False
        subj    = q['subject']
        key     = subj.split('/')[0].lower()[:3]
        field_corr = f"{key}_correct"
        field_tot  = f"{key}_total"
        conn = database.get_db_connection()
        cur  = conn.cursor()
        if is_corr:
            cur.execute(
                f"UPDATE users SET {field_corr}={field_corr}+1,"
                f"{field_tot}={field_tot}+1 WHERE id=?",
                (session['user_id'],)
            )
        else:
            cur.execute(
                f"UPDATE users SET {field_tot}={field_tot}+1 WHERE id=?",
                (session['user_id'],)
            )
        conn.commit(); conn.close()

        idx += 1
        session['current_q_idx'] = idx
        if idx >= total:
            flash("Test completed.")
            session.pop('questions')
            session.pop('current_q_idx')
            session.pop('total_qs')
            return redirect(url_for('account'))
        return redirect(url_for('test'))

    if idx >= total:
        return redirect(url_for('account'))
    q = qs[idx]
    return render_template(
        'testpage.html',
        question=q,
        qnum=f"{idx+1}/{total}",
        subject_name=q['subject'],
        username=session.get('username','')
    )

@app.route('/reportissue', methods=['GET','POST'])
@login_required
def reportissue():
    if request.method=='POST':
        cat  = request.form.get('issue')
        desc = request.form.get('description','').strip()
        if not cat or len(desc)<70:
            flash("Select category and enter at least 70 chars.")
            return redirect(url_for('reportissue'))
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute(
            "INSERT INTO issues (user_id,category,description,report_date) "
            "VALUES (?,?,?,?)",
            (session['user_id'], cat, desc, date.today().isoformat())
        )
        conn.commit(); conn.close()
        return redirect(url_for('report_thanks'))
    return render_template('reportissue.html')

@app.route('/report_thanks')
@login_required
def report_thanks():
    return render_template('thanksforreport.html')

@app.route('/changepassword', methods=['GET','POST'])
@login_required
def change_password():
    if request.method=='POST':
        curr = request.form.get('currpw','')
        new1 = request.form.get('newpw','')
        new2 = request.form.get('newpw1','')
        if new1 != new2:
            flash("New passwords do not match.")
            return redirect(url_for('change_password'))
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("SELECT password FROM users WHERE id=?", (session['user_id'],))
        u = cur.fetchone()
        if not u or u['password'] != curr:
            conn.close()
            flash("Current password incorrect.")
            return redirect(url_for('change_password'))
        cur.execute("UPDATE users SET password=? WHERE id=?", (new1, session['user_id']))
        conn.commit(); conn.close()
        flash("Password changed successfully.")
        return redirect(url_for('account'))
    return render_template('changepassword.html')

@app.route('/dlmode', methods=['GET','POST'])
@login_required
def dlmode():
    if request.method=='POST':
        mode = request.form.get('dlmode','Light')
        conn = database.get_db_connection()
        cur  = conn.cursor()
        cur.execute("UPDATE users SET theme=? WHERE id=?", (mode, session['user_id']))
        conn.commit(); conn.close()
        flash("Display mode updated.")
        return redirect(url_for('index'))
    return render_template('dlmode.html')

@app.route('/cancel_subscription')
@login_required
def cancel_subscription():
    uid = session['user_id']
    conn = database.get_db_connection()
    cur  = conn.cursor()
    cur.execute("SELECT subscription_plan FROM users WHERE id=?", (uid,))
    plan = cur.fetchone()['subscription_plan']
    if plan in ['Gold','Iconic']:
        cur.execute("UPDATE users SET subscription_plan='Basic' WHERE id=?", (uid,))
        cur.execute(
            "UPDATE payments SET status='Cancelled' "
            "WHERE user_id=? AND status='Confirmed'",
            (uid,)
        )
        conn.commit()
        flash("Subscription cancelled.")
    else:
        flash("No active paid subscription.")
    conn.close()
    return redirect(url_for('accsettings'))

@app.route('/delete_account')
@login_required
def delete_account():
    uid = session['user_id']
    conn = database.get_db_connection()
    conn.execute("DELETE FROM users WHERE id=?", (uid,))
    conn.commit(); conn.close()
    session.clear()
    return redirect(url_for('main_landing'))

if __name__ == '__main__':
    app.run(debug=True)
