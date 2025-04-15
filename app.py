from flask import Flask, render_template, redirect, url_for, request, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv  # 本地开发使用

load_dotenv()  # 加载本地.env文件

app = Flask(__name__)

# 初始化Supabase
supabase = create_client(
    os.getenv("https://rewgeacnvdxwyvghqaqg.supabase.co"),
    os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJld2dlYWNudmR4d3l2Z2hxYXFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2NDM2OTksImV4cCI6MjA2MDIxOTY5OX0.v_EU0QoJWHvGUaM7EhqBkBpuZ-xil_YtbIkYfjjf08U")
)


# 错误处理装饰器
def handle_db_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            return render_template('error.html', error_code=500), 500

    return wrapper


# 通用查询方法
def fetch_data(table, columns="*", filters=None, order_by=None):
    query = supabase.table(table).select(columns)
    if filters:
        for key, val in filters.items():
            query = query.eq(key, val)
    if order_by:
        query = query.order(order_by)
    return query.execute().data


# 路由部分
@app.route('/')
@handle_db_errors
def index():
    poems = fetch_data('poems', 'id,title,author,content', order_by='created_at')
    return render_template('index.html', poems=poems)


@app.route('/trans/<path:title>')
@handle_db_errors
def chi(title):
    poems = fetch_data('poems', filters={'title': title})
    if not poems:
        return redirect(url_for('not_found'))

    poem = poems[0]
    translations = fetch_data('translations', filters={'poem_id': poem['id']})

    return render_template('chi.html', poem=poem, translations=translations)


# 其他路由保持类似优化...

# 健康检查
@app.route('/health')
def health_check():
    try:
        supabase.table('poems').select('count', count='exact').execute()
        return 'OK', 200
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)