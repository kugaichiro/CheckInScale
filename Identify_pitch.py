import sys
import scipy.io.wavfile
import math
import numpy as np
import matplotlib.pyplot as plt
import math
from scipy import signal

from note_name import NoteName

class GetPitchFromWav:

    #コンストラクタ
    def __init__(self,file):
        #音名マップ
        #音名の配列作成
        self.noteName = NoteName()
        #音程の周波数の配列作成
        self.vecFreq = []
        self.vecFreq.append(27.5)
        semtiones = pow(2,1/12)
        for i in range(0,87):
            self.vecFreq.append(self.vecFreq[i]*semtiones)
        #二つの配列で「周波数:音名」dictを作成
        self.mapInterval = dict(zip(self.vecFreq, self.noteName))
        
        #ファイル読み込み
        self.filename = file
        
        #音源読み込み
        self.rate, self.data = scipy.io.wavfile.read(self.filename)
        #横軸（時間）を作成
        self.time = np.arange(0,self.data.shape[0]/self.rate,1/self.rate)  

        #音源を短い時間で分割
        self.seperate_time = 0.125
        self.__seperatewav(self.seperate_time)  
        
    def getTimeOfPitch(self):
        """
        音源の時間ごとの音程を取得する
        @return:時間ごとの音程の配列
        """
        timeOfPitch = {}
        for wav in self.seperateWav:
            intervalName, _ = self.__getPitch(wav, peak=10)
            if timeOfPitch.get(intervalName) is None:
                timeOfPitch[intervalName] = self.seperate_time
            else:
                timeOfPitch[intervalName] += self.seperate_time
        return timeOfPitch

    def groupPitchbyDuration(self):
        """
        """
        pitchSeparateWav = self.getPitchSeparateWav()
        current_note = None
        current_duration = 0.0
        grouped_pitches = []
        for wav in pitchSeparateWav:
            if wav is None:
                if current_note is not None:
                    grouped_pitches.append({current_note: current_duration})
                    current_note = wav
                    current_duration = 0.0
            else:
                if current_note is None:
                    current_note = wav
                    current_duration = self.seperate_time
                elif current_note == wav:
                    current_duration += self.seperate_time
                else:
                    grouped_pitches.append((current_note, current_duration))
                    current_note = wav
                    current_duration = self.seperate_time
        return pitchSeparateWav

    def getPitchSeparateWav(self):
        """
        音源の時間ごとの音程を取得する
        @return:時間ごとの音程の配列
        """
        pitchSeparateWav = []
        for wav in self.seperateWav:
            intervalName, _ = self.__getPitch(wav, peak=10)
            pitchSeparateWav.append(intervalName)
        return pitchSeparateWav

    def __seperatewav(self, seperate_time):
        """
        @seperate_time: 分割する時間[s]
        """
        #分割するサンプル数
        sepearte_sample = int(self.rate * seperate_time)
        #分割数
        num_seperate = math.ceil(self.data.shape[0] / sepearte_sample)
        
        #分割した波形を格納する配列
        self.seperateWav = []
        
        for i in range(num_seperate):
            start = i * sepearte_sample
            end = (i + 1) * sepearte_sample
            if end > self.data.shape[0]:
                end = self.data.shape[0]
            self.seperateWav.append(self.data[start:end])
        

            
    #FFTを処理した波形を表示
    def __getPitch(self, wav, peak):

        # ステレオ音源の場合はモノラルに変換する
        if wav.ndim > 1:
            wav = np.mean(wav, axis=1)

        fftData = np.abs(np.fft.rfft(wav))
        fftFreq = np.fft.rfftfreq(wav.shape[0], d=1.0 / self.rate)

        #ピーク値を取得
        # argrelmaxはタプルを返すため、インデックス配列だけを取り出す
        peak_indices = signal.argrelmax(fftData, order=peak)[0]

        # ピークがない区間では、DC成分以外の最大値を候補にする
        if peak_indices.size == 0:
            if fftData.size <= 1 or np.all(fftData[1:] == 0):
                return None, np.array([])
            peak_indices = np.array([np.argmax(fftData[1:]) + 1])

        #最もゲインの大きいピークの周波数を返す
        maxPeakFreq = self.__getPeakFreq(
            fftFreq[peak_indices], fftData[peak_indices]
        )
        #その周波数に最も近い音名を返す
        intervalName = self.__searchInterval(maxPeakFreq)
        return intervalName, fftFreq[peak_indices]
        
    
   #searchInterval(周波数)
    def __searchInterval(self,freq):
        """
        @freq  :音程を知りたい周波数
        @return:音程を返す
        """
        #平均率で最も近い周波数を検索
        nearfreq = self.__getNearestValue(self.vecFreq,freq)
        #その音名
        nameInterval = self.mapInterval[nearfreq]
        return nameInterval
        
    #最も近い値を返す
    def __getNearestValue(self,list, num):
        """
        概要: リストからある値に最も近い値を返却する関数
        @param list: データ配列
        @param num: 対象値
        @return 対象値に最も近い値
        """
        # リスト要素と対象値の差分を計算し最小値のインデックスを取得
        idx = np.abs(np.asarray(list) - num).argmin()
        return list[idx]
        
    #最もゲインの大きいピークの周波数を返す(周波数配列、ゲイン配列)
    def __getPeakFreq(self,peakFreq,peakGain):
        mapMaxPeak = dict(zip(peakGain,peakFreq))
        maxPeakValue = np.amax(peakGain)
        return mapMaxPeak[maxPeakValue]

if __name__ == "__main__":
    wav_file = "shidenbeatsmusic-acoustic-guitar-short-intro-ish-live-recording-163329.wav"
    

    pitchIdentifier = GetPitchFromWav(wav_file)
    
    print(pitchIdentifier.getTimeOfPitch())
    
