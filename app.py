from flask import Flask, render_template, redirect, url_for, request
import os
from supabase import create_client

app = Flask(__name__)

# 获取环境变量
supabase_url = os.getenv('https://rewgeacnvdxwyvghqaqg.supabase.co')
supabase_key = os.getenv('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJld2dlYWNudmR4d3l2Z2hxYXFnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ2NDM2OTksImV4cCI6MjA2MDIxOTY5OX0.v_EU0QoJWHvGUaM7EhqBkBpuZ-xil_YtbIkYfjjf08U')

# 初始化 Supabase 客户端
supabase = create_client(supabase_url, supabase_key)


# 首页路由
@app.route('/')
def index():
    try:
        response = supabase.table('poems').select('id, title, author, content').execute()
        poems = response.data
        return render_template('index.html', poems=poems)
    except Exception as e:
        return f"Error fetching poems: {e}", 500


# 显示诗歌的翻译版本页面路由
@app.route('/trans/<path:title>')
def chi(title):
    try:
        # 获取诗歌信息
        poem_response = supabase.table('poems').select('*').eq('title', title).execute()
        poem = poem_response.data[0] if poem_response.data else None

        if poem:
            # 获取翻译信息
            translations_response = supabase.table('translations').select('*').eq('poem_id', poem['id']).execute()
            translations = translations_response.data
            return render_template('chi.html', poem=poem, translations=translations)
        else:
            return redirect(url_for('not_found'))
    except Exception as e:
        return f"Error fetching translations: {e}", 500


# 显示翻译者详细信息页面路由
@app.route('/detail/<path:translator>')
def detail(translator):
    try:
        translator_response = supabase.table('translations').select('*').eq('translator', translator).execute()
        translator_info = translator_response.data[0] if translator_response.data else None
        if translator_info:
            return render_template('detail.html', translator_info=translator_info)
        else:
            return "没有找到译者信息。", 404
    except Exception as e:
        return f"Error fetching translator info: {e}", 500


@app.route('/search')
def search():
    search_title = request.args.get('title', '')
    if not search_title:
        return redirect(url_for('index'))

    try:
        response = supabase.table('poems').select('id, title, author, content').ilike('title',
                                                                                      f'%{search_title}%').execute()
        poems = response.data
        return render_template('index.html', poems=poems)
    except Exception as e:
        return f"Error searching poems: {e}", 500


@app.route('/dai')
def dai():
    try:
        response = supabase.table('dai').select('did, authorship, author, content').execute()
        dais = response.data
        return render_template('dai.html', dais=dais)
    except Exception as e:
        return f"Error fetching dai: {e}", 500


@app.route('/not_found')
def not_found():
    return render_template('nf.html'), 404


if __name__ == '__main__':
    app.run(debug=True)