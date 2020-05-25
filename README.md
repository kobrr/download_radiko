# auto_download_radiko
ラジコの番組を録音し、番組情報や出演者・ラジオ局情報メタデータ付きのmp3ファイルとして保存できます。
Herokuなどを利用すれば、毎週のスケジュール実行もできます。(ファイル保存はDropbox APIなどで)

# Output
![file info](https://user-images.githubusercontent.com/58103830/82830715-74aca580-9ef1-11ea-96cc-82976d919241.png)

# Requirement
ffmpeg version 4.2.2 Copyright (c) 2000-2019 the FFmpeg developers
eyeD3==0.9.5

python==3.7.4
    urllib
    os
    sys
    re==2.2.1
    subprocess
    base64
    requests==2.22.0
    numpy
    datetime
    beautifulsoup4==4.8.0

# Flow
  1: https://radiko.jp/v2/api/auth1 にGETリクエストしてトークンを取得
  2: https://radiko.jp/v2/api/auth2 にGETリクエストしてトークンを認証
  3: 2で認証したトークンを使って番組を再生&録音
  refer to: https://gist.github.com/ji6czd/f86440200ba286f1f7af2e103dd430ff


# Author
  Ryosuke Kobayashi

# License
  コードや保存したmp3ファイルは非営利目的に限ります。
