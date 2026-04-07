from flask import Flask, request,redirect,render_template,session
import pymysql

app = Flask(__name__)
app.secret_key = "123"

def make_db():
    conn = pymysql.connect(
        host = "localhost",
        user = "root",
        passwd = ""
    )
    c = conn.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS flask20")
    conn.commit()
    conn.close()

def connector():
    return pymysql.connect(
        host="localhost",
        user="root",
        passwd="",
        database="flask20"
    )

def init_db():
    conn = connector()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS questions(
              id INT AUTO_INCREMENT PRIMARY KEY,
              nickname TEXT,
              question_title TEXT,
              question_content TEXT
              )
              """)
    c.execute("""CREATE TABLE IF NOT EXISTS users(
              user_name VARCHAR(30),
              user_password TEXT
              )
              """)
    c.execute("""CREATE TABLE IF NOT EXISTS likes(
              like_count INT AUTO_INCREMENT PRIMARY KEY,
              like_user TEXT,
              like_post INT
              )
              """)
    c.execute("""CREATE TABLE IF NOT EXISTS comments(
              id INT AUTO_INCREMENT PRIMARY KEY,
              comment_name TEXT,
              comment_content TEXT,
              comment_id INT
              )
              """)
    conn.commit()
    conn.close()

@app.route('/')
def home():
    name = session.get("user")
    conn = connector()
    c = conn.cursor()
    c.execute("SELECT * FROM questions ORDER by id DESC")
    questions = c.fetchall()
    conn.commit()
    conn.close()
    return render_template('qna_index.html',questions=questions,name=name)

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template('qna_register.html')
    conn = connector()
    c = conn.cursor()
    nickname = request.form["nickname"]
    password = request.form["password"]
    c.execute("SELECT * FROM users WHERE user_name = %s",(nickname,))
    is_exists = c.fetchone()
    if is_exists:
        fail_register = "이미 존재하는 회원 이름입니다"; return render_template('qna_register.html',fail_register=fail_register)
    c.execute("INSERT INTO users (user_name,user_password) VALUES (%s,%s)",(nickname,password))
    conn.commit()
    conn.close()
    session["user"] = nickname
    return redirect('/')

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template('qna_login.html')
    conn = connector()
    c = conn.cursor()
    nickname = request.form["nickname"]
    password = request.form["password"]
    c.execute("SELECT * FROM users WHERE user_name = %s AND user_password = %s",(nickname,password))
    is_login = c.fetchone()
    if not is_login:
        fail_login = "닉네임과 비밀번호를 다시 확인하십시오."; return render_template('qna_login.html',fail_login=fail_login)
    conn.commit()
    conn.close()
    session["user"] = nickname
    return redirect('/')

@app.route('/write',methods=["GET","POST"])
def write():
    if request.method=="GET":
        return render_template('qna_write.html')
    nickname = session.get("user")
    if not nickname:
        return "해당 기능은 로그인이 필요합니다."
    conn=connector()
    c=conn.cursor()
    title = request.form["title"]
    content = request.form["content"]
    c.execute("INSERT INTO questions (nickname,question_title,question_content) VALUES (%s,%s,%s)",(nickname,title,content))
    conn.commit()
    conn.close()
    return redirect('/') 

@app.route('/detail/<int:question_id>')
def detail(question_id):
    conn = connector()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE id = %s",(question_id,))
    question = c.fetchone()
    c.execute("SELECT * FROM likes WHERE like_post = %s",(question_id,))
    likes = c.fetchall()
    c.execute("SELECT * FROM comments WHERE comment_id = %s",(question_id,))
    comments = c.fetchall()
    conn.close()
    return render_template('qna_detail.html',question=question,likes=likes,comments=comments)

@app.route('/detail/<int:question_id>/delete',methods=["POST"])
def detail_delete(question_id):
    conn = connector()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE id = %s",(question_id,))
    is_delete = c.fetchone()
    nickname = session.get("user")
    if not nickname:
        return "권한부족"
    if nickname == is_delete[1]:
        c.execute("DELETE FROM questions WHERE id = %s",(question_id,))
        conn.commit()
        conn.close()
        return redirect('/')
    conn.commit()
    conn.close()
    return "권한부족"
    
@app.route('/detail/<int:question_id>/like',methods=["POST"])
def detail_like(question_id):
    conn = connector()
    c = conn.cursor()
    nickname = session.get("user")
    c.execute("SELECT * FROM likes WHERE like_user = %s AND like_post = %s",(nickname,question_id))
    is_like = c.fetchone()
    if is_like:
        return "이미 좋아요를 눌렀습니다."
    c.execute("INSERT INTO likes (like_user,like_post) VALUES (%s,%s)",(nickname,question_id))
    conn.commit()
    conn.close()
    return redirect('/detail/%s'%(question_id))

@app.route('/detail/<int:question_id>/comment',methods=["POST"])
def comment_comment(question_id):
    conn=connector()
    c = conn.cursor()
    nickname = session.get("user")
    if not nickname:
        return "로그인하고와"
    content = request.form["content"]
    c.execute("INSERT INTO comments (comment_name,comment_content,comment_id) VALUES (%s,%s,%s)",(nickname,content,question_id))
    conn.commit()
    conn.close()
    return redirect('/detail/%s'%(question_id))
make_db()
init_db()

app.run(host="localhost",port=5050,debug=True)



