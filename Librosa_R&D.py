import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from glob import glob
import librosa
arr=[]
filename_arr=[]
value = []
count =0
data_dir = 'D:/Python programing ide/dataset'
audio_files = glob(data_dir + '/*.wav')
for i in range(0,len(audio_files),1):
    filename_arr.append(audio_files[i])
for i in range(0,len(audio_files),1):
    audio, sfreq = librosa.load(audio_files[i])
    time = np.arange(0, len(audio))/sfreq
    fig, ax = plt.subplots()
    ax.plot(time, audio)
    ax.set(xlabel='Time (in sec)', ylabel='Amplitude')
    plt.show(block=False)
    plt.pause(3)
    plt.close()
    tempo, beat_frames = librosa.beat.beat_track(y=audio, sr=sfreq)
    arr.append(tempo)
    print('Estimated tempo: {:.2f} beats per minute'.format(tempo))
    beat_times = librosa.frames_to_time(beat_frames, sr=sfreq)
    print(beat_times)

df = pd.DataFrame({'File Names': filename_arr ,'Tempo detection using librosa ': arr})
writer = pd.ExcelWriter('librosa.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()

f1 = pd.read_excel("librosa.xlsx")
f2 = pd.read_excel("D:/Python programing ide/result.xlsx")


f3 = f1.merge(f2,left_on=None, right_on=None, left_index=False, right_index=False )

f3.to_excel("Librosa_Final.xlsx", index=False)
xl= pd.ExcelFile('Librosa_Final.xlsx')
get_sheet = xl.parse('Sheet1')
for j in range(0,len(audio_files),1):
    get_var = get_sheet['RESULT'][j]
    value.append(get_var)

for j in range(0,len(audio_files),1):
    a = arr[j]
    b = value[j]
    upper_bound = b + b*0.02
    lower_bound = b - b*0.02
    if(a>lower_bound and a<upper_bound):
        count = count+1
result = (count/(len(audio_files))) * 100
print("So the precission of Librosa is",result,"% on a total of",len(audio_files),"files")
