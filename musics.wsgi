#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# DB を変更，ID, 好きな曲，アーティスト，ジャンル，おすすめポイント
# 詳細ページを実装
# デザインを実装

import sys
import os
import io
import re
import textwrap

# CGIモジュールをインポート
import cgi
import cgitb
cgitb.enable()

localhost=False

# sqlite3（SQLサーバ）モジュールをインポート
import sqlite3

# データベースファイルのパスを設定
app_dir = os.path.dirname(os.path.abspath(__file__))
dbname = os.path.join(app_dir, 'data.db')

# テーブルの作成
def createTable():
    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    # テーブルの作成
    create_musics_table = 'create table if not exists musics (musicID int, title varchar(64), band varchar(64), jenre varchar(64), recommend varchar(128))'
    cur.execute(create_musics_table)
    # コミット（変更を確定）
    con.commit()
    
    # カーソルと接続を閉じる
    cur.close()
    con.close()

createTable()

# sumikaの曲をデータベースへ登録
def ini_registerMusics(last_id):
    import csv
    open_csv = open("musics.csv")
    read_csv = csv.reader(open_csv)
    
    rows = []
    for i, row in enumerate(read_csv):
        rows.append(row)
        registerMusic(last_id+1+i, row[0], row[1], row[2], '')
    open_csv.close()
    
# 曲の情報のデータベースへの登録
def registerMusic(music_id, music_title, band_name, jenre, recommend):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    # SQL文（insert）の作成と実行
    sql = 'insert into musics (musicID, title, band, jenre, recommend) values (?,?,?,?,?)'
    cur.execute(sql, (music_id, music_title, band_name, jenre, recommend))
    con.commit()

    cur.close()
    con.close()

# 本の情報の登録一覧の取得
def getAllmusics():
    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    # SQL文（select）の作成と実行
    sql = 'select * from musics'
    cur.execute(sql)
    lists = cur.fetchall()

    cur.close()
    con.close()

    return lists

def getSearchtitles(title):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    # SQL文（select）の作成と実行
    sql = 'select * from musics where title like ?'
    
    cur.execute(sql, ('%'+str(title)+'%',))
    lists = cur.fetchall()
    cur.close()
    con.close()

    return lists

def getSearchauthors(author):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    # SQL文（select）の作成と実行
    sql = 'select * from musics where band like ?'
    
    cur.execute(sql, ('%'+str(author)+'%',))
    lists = cur.fetchall()
    cur.close()
    con.close()

    return lists

def getSearchjenres(jenre):
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    con.text_factory = str

    # SQL文（select）の作成と実行
    sql = 'select * from musics where jenre like ?'
    
    cur.execute(sql, ('%'+str(jenre)+'%',))
    lists = cur.fetchall()
    cur.close()
    con.close()

    return lists

def removeMusics(music_id):
    # データベース接続とカーソル生成
    con = sqlite3.connect(dbname)
    cur = con.cursor()

    # SQL文（select）の作成と実行
    sql = 'delete from musics where musicID = ?'
    
    cur.execute(sql, (music_id,))
    con.commit()
    cur.close()
    con.close()

# CSSファイルなどを送信（リファレンスWEBサーバ実行時のみ使用）
def serveFile(environ,start_response):
    # 拡張子とコンテンツタイプ（必要に応じて追加すること）
    types = {'.css': 'text/css', '.jpg': 'image/jpg', '.png': 'image/png'}
    
    # static ディレクトリ以下の指定ファイルを開いてその内容を返す．
    # ファイルが無ければエラーを返す．
    #
    assert(re.match('/static/', environ['PATH_INFO']))
    filepath = '{dir}/{path}'.format(dir=app_dir, path=environ['PATH_INFO'])
    ext  = os.path.splitext(filepath)[1]
    
    if os.path.isfile(filepath) and ext in types:
        try:
            with open(filepath, "rb") as f:
                r = f.read()
            binary_stream = io.BytesIO(r)
        except:
            start_response('500 Internal Server Error', [('Content-Type', 'text/plain')])
            return [b"Internal server error"]
    else:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return [b"Not found."]

    start_response('200 OK', [('Content-Type', types[ext])])
    return binary_stream

# アプリケーション本体
def application(environ,start_response):
    
    if localhost and re.match('/static/', environ['PATH_INFO']):
        ''' リファレンスWEBサーバ実行時のみ
             このwsgiスクリプトを実行しているカレントディレクトリ以下に
             static というディレクトリを作って，default.cssというファイルを置いておくと，
             http://localhost:8080/static/default.css でファイルがダウンロードできる．
        '''
        return serveFile(environ,start_response)
    
    # HTML（共通テンプレート）
    tmpl = textwrap.dedent('''
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>WSGI テスト</title>
        <link rel="stylesheet" href="/static/default.css"> 
    </head>
    <body>
    <div class="header">
        <p>share musics</p>
        <div class="search-form">
        <form>
            <label>
                <input type="text" name="title" placeholder="曲名">
            </label>
            <button type="submit" name="title_search"></button>
        </form>
        </div>
        <div class="search-form">
        <form>
            <label>
                <input type="text" name="author" placeholder="アーティスト名">
            </label>
            <button type="submit" name="author_search"></button>
        </form>
        </div>
        <div class="search-form">
        <form>
            <label>
            <select name="jenre">
                <option value="">ジャンル</option>
                <option value="J-POP">J-POP</option>
                <option value="ロック">ロック</option>
                <option value="K-POP">K-POP</option>
                <option value="EDM">EDM</option>
                <option value="アニソン">アニソン</option>
                <option value="ボカロ">ボカロ</option>
            </select>
            </label>
            <button type="submit" name="jenre_search"></button>
        </form>
        </div>
        <div class="to-index">
        <form>
            <button type="submit" name="index" class="btn-to-index"><span>一覧ページ</span></button>
        </form>
        </div>
    </div>
    {body}
    <a href="./book_v9.wsgi">曲の登録ページに戻る</a>
    </body>
    </html>
    ''')
    colum = f'<tr><th>曲名</th><th>アーティスト名</th><th>ジャンル</th></tr>\n'

    # フォームデータを取得
    form = cgi.FieldStorage(environ=environ,keep_blank_values=True)

    if 'ini_music_register' in form:
        musics_list = getAllmusics()
        if (musics_list == []):
            last_id = 0
        else:
            last_id = int(musics_list[-1][0])
        ini_registerMusics(last_id)
        
        msg = '登録が完了しました！'
        colum = f'<tr><th>本の番号</th><th>タイトル</th><th>著者名</th></tr>\n'
        # データベースの登録情報一覧の取得
        musics_list = getAllmusics()

        s_b_list = ''
        for i, row in enumerate(musics_list):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <p>{message}</p>
        <h2>一覧表示</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(message=msg, blist=s_b_list)

    elif 'index' in form:
        musics_list = getAllmusics()
        # 一覧のHTML形式への変換
        s_b_list = ''
        for i, row in enumerate(musics_list):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <h2>一覧ページ</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(blist=s_b_list)

    elif 'title_search' in form:
        # フォームデータから各フィールド値を取得
        title = form.getvalue("title")

        if title != '':
            searched_musics = getSearchtitles(title)
            msg = '曲名で検索しました'
        else:
            searched_musics = getAllmusics()
            msg = '指定の曲名に合う楽曲が見つかりませんでした'

        s_b_list = ''
        for i, row in enumerate(searched_musics):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <p>{message}</p>
        <h2>曲の検索結果</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(message=msg, blist=s_b_list)

    elif 'jenre_search' in form:
        # 入力フォームで登録ボタンがクリックされた場合

        # フォームデータから各フィールド値を取得
        jenre = form.getvalue("jenre")

        if jenre != '':
            searched_musics = getSearchjenres(jenre)
            msg = 'ジャンルで検索しました'
        else:
            searched_musics = getAllmusics()
            msg = '指定のジャンルに合う楽曲が見つかりませんでした'

        s_b_list = ''
        for i, row in enumerate(searched_musics):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <p>{message}</p>
        <h2>ジャンルによる検索結果</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(message=msg, blist=s_b_list)

    
    elif 'author_search' in form:
        # 入力フォームで登録ボタンがクリックされた場合

        # フォームデータから各フィールド値を取得
        author = form.getvalue("author")

        if author != '':
            searched_musics = getSearchauthors(author)
            msg = 'アーティスト名で検索しました'
        else:
            searched_musics = getAllmusics()
            msg = '指定のアーティスト名に合う検索が見つかりませんでした'

        s_b_list = ''
        for i, row in enumerate(searched_musics):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <p>{message}</p>
        <h2>アーティスト名による検索結果</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(message=msg, blist=s_b_list)

    elif 'select_delete' in form:
        
        msg = "削除したよ！"
        delmusicnum = form.getvalue("delb")
        
        removeMusics(int(delmusicnum))
        musics_list = getAllmusics()
        s_b_list = ''
        for i, row in enumerate(musics_list):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <p>{message}</p>
        <h2>一覧表示</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(message=msg, blist=s_b_list)

    
    elif 'show' in form:
        show_id = form.getvalue("show")[0]
        # フォームデータから各フィールド値を取得
        musics_list = getAllmusics()
        a_music = musics_list[int(show_id)]
        song_name = textwrap.dedent('''
        <div class="show-name">
            {s_name}
        </div>
        ''').format(s_name=str(a_music[1]))
        author = textwrap.dedent('''
        <div class="show-artist">
            {a_name}
        </div>
        ''').format(a_name=str(a_music[2]))
        genre = textwrap.dedent('''
        <div class="show-genre">
            {g_name}
        </div>
        ''').format(g_name=str(a_music[3]))
        song_rec = textwrap.dedent('''
        <div class="show-recommend">
            {r_name}
        </div>
        ''').format(r_name=str(a_music[4]))
        delete_button = textwrap.dedent('''
        <form>
            <input type="hidden" name="delb" value="{dvalue}">
            <th><button type="submit" name="select_delete">削除</button></th>
        </form>
        ''').format(dvalue=int(a_music[0]))
        print_music = f'{song_name}{author}{genre}{song_rec}{delete_button}\n'
        bcontent = textwrap.dedent('''
        <div class="ol1">
        <h2>詳細ページ</h2>
            {colum}
            {print_music}
        </div>
        ''').format(colum=colum, print_music=print_music)
    elif 'new_book_register' in form:
        # 入力フォームで登録ボタンがクリックされた場合
        # データベースの登録情報一覧の取得
        books_list = getAllmusics()
        
        # フォームデータから各フィールド値を取得
        if len(books_list) == 0:
            v1 = 0
        else:
            v1 = books_list[-1][0]+1
        v2 = form.getvalue("b_v2")
        v3 = form.getvalue("b_v3")
        v4 = form.getvalue("b_v4")
        v5 = form.getvalue("b_v5")

        if (v2 != '' or v3 != '' or v4 != ''):
            if v5 != '':
                registerMusic(v1, v2, v3, v4, v5)  # データベースへの登録
            else:
                registerMusic(v1, v2, v3, v4, '')  # データベースへの登録
            msg = '登録しました。'
            print(v2, v3 == '', v4, v5)
        else:
            msg = '登録失敗：空になっている入力項目があります。'

        musics_list = getAllmusics()

        s_b_list = ''
        for i, row in enumerate(musics_list):
            
            name = textwrap.dedent('''
            <div class="song-name">
                ♬ {s_name}
            </div>
            ''').format(s_name=str(row[1]))

            band = textwrap.dedent('''
            <div class="band-name">
                ✏︎ {a_name}
            </div>
            ''').format(a_name=str(row[2]))

            genre = textwrap.dedent('''
            <div class="jenre-name">
                {j_name}
            </div>
            ''').format(j_name=str(row[3]))
            show_button = textwrap.dedent('''
            <form>
                <input type="hidden" name="show" value="{svalue}">
                <th><button type="submit" name="show">詳細</button></th>
            </form>
            ''').format(svalue=i)
            delete_button = textwrap.dedent('''
            <form>
            <input type="hidden" name="delb" value="{dvalue}">
                <th><button type="submit" name="select_delete">削除</button></th>
            </form>
            ''').format(dvalue=int(row[0]))
            
            s_b_list += f'<div class="a_music">{genre}<div class="name-band">{name}{band}</div><div class="sh-de-btn">{show_button}{delete_button}</div></div>\n'

        bcontent = textwrap.dedent('''
        <p>{message}</p>
        <h2>一覧表示</h2>
        <div class="form1">
        {blist}
        </div>
        ''').format(message=msg, blist=s_b_list)

    else:
        # デフォルトページ（入力フォーム表示）
        jenreform = textwrap.dedent('''
        <select name="b_v4" class="input-content">
            <option value="">Jenre</option>
            <option value="J-POP">J-POP</option>
            <option value="ロック">ロック</option>
            <option value="K-POP">K-POP</option>
            <option value="EDM">EDM</option>
            <option value="アニソン">アニソン</option>
            <option value="ボカロ">ボカロ</option>
        </select>
        ''')
        # HTML（入力フォーム部分）
        bcontent = textwrap.dedent('''
        情報を登録する
        <form>
            <button type="submit" name="ini_music_register">sumikaの登録</button>
        </form>
        <div class="inputform">
            <form>
            <p><input type="text" name="b_v2"  class="input-content" placeholder="曲名"></p>
            <p><input type="text" name="b_v3"  class="input-content" placeholder="アーティスト名"></p>
            <p>{jform}</p>
            <p><textarea name="b_v5" class="input-text"  placeholder="おすすめポイント"></textarea></p>
            <button type="submit" name="new_book_register">登録</button>
            </form>
        </div>
        ''').format(jform=jenreform)

    html = tmpl.format(body=bcontent)
    html = html.encode('utf-8')

    # レスポンス
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(html))) ])
    return [html]

# リファレンスWEBサーバを起動
#  ファイルを直接実行する（python3 sample.wsgi）と，
#  リファレンスWEBサーバが起動し，http://localhost:8080 にアクセスすると
#  このサンプルの動作が確認できる．
#  コマンドライン引数にポート番号を指定（python3 sample.wsgi ポート番号）した場合は，
#  http://localhost:ポート番号 にアクセスする．
from wsgiref import simple_server
if __name__ == '__main__':
    port = 8080
    localhost = True
    if len(sys.argv) == 2:
        port = int(sys.argv[1])

    server = simple_server.make_server('', port, application)
    server.serve_forever()