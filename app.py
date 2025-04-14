from flask import Flask, render_template, redirect, url_for
import mysql.connector
from mysql.connector import Error
from flask import request

app = Flask(__name__)

# 数据库配置信息
db_config = {
    'host': 'localhost',
    'database': 'poetry_db',
    'user': 'root',
    'password': '123456',
    'auth_plugin': 'mysql_native_password',
    'buffered': True,
}

# 获取数据库连接的函数
def get_db_connection():
    connection = None
    try:
        connection = mysql.connector.connect(**db_config)
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

# 首页路由
@app.route('/')
def index():
    connection = get_db_connection()
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute("SELECT id, title, author, content FROM poems")
        poems = cursor.fetchall()
        cursor.close()
        connection.close()
        return render_template('index.html', poems=poems)
    else:
        return "Failed to connect to the database", 500

# 显示诗歌的翻译版本页面路由
@app.route('/trans/<path:title>')
def chi(title):
    connection = get_db_connection()
    poem = None
    translations = []
    if connection:
        cursor = connection.cursor(buffered=True)  # 使用缓冲游标
        try:
            cursor.execute("SELECT * FROM poems WHERE title = %s", (title,))
            poem = cursor.fetchone()
            if poem:
                cursor.execute("SELECT * FROM translations WHERE poem_id = %s", (poem[0],))
                translations = cursor.fetchall()
        finally:
            cursor.close()  # 确保在 finally 块中关闭游标
        connection.close()  # 同样在 finally 块中关闭连接
        if poem and translations:
            return render_template('chi.html', poem=poem, translations=translations)
        else:
            return redirect(url_for('not_found'))
    return "数据库连接失败。", 500

# 显示翻译者详细信息页面路由
@app.route('/detail/<path:translator>')
def detail(translator):
    connection = get_db_connection()
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM translations WHERE translator = %s", (translator,))
        translator_info = cursor.fetchone()
        cursor.close()
        connection.close()
        if translator_info:
            return render_template('detail.html', translator_info=translator_info)
        else:
            return "没有找到译者信息。", 404
    else:
        return "数据库连接失败。", 500

@app.route('/search')
def search():
    search_title = request.args.get('title', '')  # 获取搜索关键词
    if not search_title:
        return redirect(url_for('index'))

    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT id, title, author, content FROM poems WHERE title LIKE %s", ('%' + search_title + '%',))
            poems = cursor.fetchall()
        except Error as e:
            app.logger.error(f"Database query error: {e}")
            return "数据库查询失败。", 500
        finally:
            cursor.close()
            connection.close()

        if poems:
            return render_template('index.html', poems=poems)
        else:
            return redirect(url_for('not_found'))
    else:
        return "数据库连接失败。", 500

@app.route('/dai')
def dai():
    connection = get_db_connection()
    if connection.is_connected():
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT did, authorship, author, content FROM dai")
            dais = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        if dais:
            return render_template('dai.html', dais=dais)
        else:
            return "没有找到待考证的诗歌。", 404
    else:
        return "数据库连接失败。", 500

@app.route('/not_found')
def not_found():
    return render_template('nf.html'), 404


if __name__ == '__main__':
    app.run(debug=True)