import gdown
import zipfile
import os
from fontTools import ttLib

# Google Driveの共有リンクからファイルIDを抽出
file_id = '1eLmitieWVp71JPKb2nCO_9iRRj8_pTx_'
url = f'https://drive.google.com/uc?id={file_id}'

# ダウンロード先のファイルパス
zip_path = 'downloaded.zip'

# Google DriveからZIPファイルをダウンロード
gdown.download(url, zip_path, quiet=False)

# ZIPファイルを解凍して、.ttfファイルを抽出
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    # ZIP内のファイルリストを取得
    file_list = zip_ref.namelist()
    # .ttfファイルをフィルタリング
    ttf_files = [f for f in file_list if f.lower().endswith('.ttf')]
    
    # .ttfファイルを抽出
    for ttf in ttf_files:
        zip_ref.extract(ttf)
        print(f'Extracted: {ttf}')
        # フォントファイルを読み込み、情報を表示
        font = ttLib.TTFont(ttf)
        print(f'Font Name: {font["name"].getName(1, 3, 1).toStr()}')
        print(f'Font Family: {font["name"].getName(1, 3, 1).toStr()}')
        print('-' * 40)

# ダウンロードしたZIPファイルを削除（必要に応じて）
os.remove(zip_path)
