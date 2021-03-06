# About
ラジコで放送されるFM/AMラジオ番組を録音し、番組情報や出演者、ラジオ局情報のメタデータ付き.mp3ファイルとして保存できます。<br>
月曜日になると放送番組リストが更新されてしまうようなので、該当週の日曜日までにダウンロードしておく必要があります。<br>
クラウドにDeployすれば、毎週のスケジュール実行も可<br>

# Output
![file info](https://user-images.githubusercontent.com/58103830/82830715-74aca580-9ef1-11ea-96cc-82976d919241.png)

# Usage
&emsp;main(station, title)<br>
&emsp;station: "station_id_table.ipynb"を参照<br>
&emsp;title: ラジコ番組表上のタイトル<br>

# Requirements
ffmpeg version 4.2.2 Copyright (c) 2000-2019 the FFmpeg developers<br>
eyeD3==0.9.5<br>
python==3.7.4<br>
&emsp;urllib<br>
&emsp;os<br>
&emsp;sys<br>
&emsp;subprocess<br>
&emsp;base64<br>
&emsp;numpy<br>
&emsp;datetime<br>
&emsp;re==2.2.1<br>
&emsp;requests==2.22.0<br>
&emsp;beautifulsoup4==4.8.0<br>

# Flow
&emsp;1: https://radiko.jp/v2/api/auth1 にGETリクエストしてトークンを取得<br>
&emsp;2: https://radiko.jp/v2/api/auth2 にGETリクエストしてトークンを認証<br>
&emsp;3: 2で認証したトークンを使って番組を再生&録音<br>
&emsp;Reference: https://gist.github.com/ji6czd/f86440200ba286f1f7af2e103dd430ff<br>

# Author
Ryosuke Kobayashi<br>

# License
コードや保存したmp3ファイルは非営利目的に限ります。<br>
