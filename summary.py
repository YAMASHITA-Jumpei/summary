
from yt_dlp import YoutubeDL
import ffmpeg
import speech_recognition as sr
from pysummarization.nlpbase.auto_abstractor import AutoAbstractor
from pysummarization.tokenizabledoc.mecab_tokenizer import MeCabTokenizer
from pysummarization.abstractabledoc.top_n_rank_abstractor import TopNRankAbstractor

# 動画ダウンロード
ydl_video_opts = {'outtmpl': 'material'}
with YoutubeDL(ydl_video_opts) as ydl:
    result = ydl.download(['https://www.youtube.com/watch?v=4xAfYBt4314&t=1s'])

# 拡張子変換
material = ffmpeg.input('material.webm')
material = ffmpeg.output(material, 'material.wav')
ffmpeg.run(material)

# 動画分割
material = 'material.wav'
info = ffmpeg.probe(material)
duration = float(info['streams'][0]['duration'])
split_time = 180  # 180秒（3分）ごと
current = 0
idx = 1
while current < duration:
    start = current
    stream = ffmpeg.input(material, ss=start, t=split_time)
    stream = ffmpeg.output(stream, f'split{idx}.wav', c='copy')
    ffmpeg.run(stream)
    idx += 1
    current += split_time

# 文字起こし
r = sr.Recognizer()
num = 1
while num < idx:
    with sr.AudioFile(f'split{num}.wav') as source:
        audio = r.record(source)
    text = r.recognize_google(audio, language='ja-JP')
    f = open('text.txt', 'a', encoding='UTF-8')
    f.write(text+'\n')
    num += 1
f.close()

# 要約
with open('text.txt', encoding='utf-8') as f:
    contents = f.readlines()
document = ''.join(contents)
auto_abstractor = AutoAbstractor()
auto_abstractor.tokenizable_doc = MeCabTokenizer()
auto_abstractor.delimiter_list = ["でした", "ます", "です"]
abstractable_doc = TopNRankAbstractor()
result_dict = auto_abstractor.summarize(document, abstractable_doc)

f = open('summary.txt', 'a', encoding='UTF-8')
for sentence in result_dict["summarize_result"]:
    f.write(sentence+'\n')

print('==========アプリケーション正常に完了しました==========')
