import madmom, scipy.stats
import numpy as np
from glob import glob
import pandas as pd
arr=[]
filename_arr=[]
value = []
count =0

f2 = pd.read_excel("D:/Python programing ide/result.xlsx")
print(f2)
data_dir = 'D:/Python programing ide/dataset'
audio_files = glob(data_dir + '/*.wav')
for i in range(0,len(audio_files),1):
    filename_arr.append(audio_files[i])
for i in range(0,len(audio_files),1):
    beats = madmom.features.beats.RNNBeatProcessor()(audio_files[i])
    when_beats = madmom.features.beats.BeatTrackingProcessor(fps=100)(beats)
    m_res = scipy.stats.linregress(np.arange(len(when_beats)),when_beats)
    first_beat = m_res.intercept
    beat_step = m_res.slope
    print(first_beat)
    print(beat_step)
    arr.append(60/beat_step)
    print("bpm = ", 60/beat_step)

df = pd.DataFrame({'File Names': filename_arr ,'Tempo detection using madmom ': arr})
writer = pd.ExcelWriter('madmom.xlsx', engine='xlsxwriter')
df.to_excel(writer, sheet_name='Sheet1', index=False)
writer.save()


f1 = pd.read_excel("madmom.xlsx")
f2 = pd.read_excel("D:/Python programing ide/result.xlsx")


# f3 = f1.merge(f2,left_on=None, right_on=None, left_index=False, right_index=False )
f3 = pd.merge(f1, f2, on = "File Names" )
f3.to_excel("Madmom_Final.xlsx", index=False)
xl= pd.ExcelFile('Madmom_Final.xlsx')
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
print("So the precission of Madmom is",result,"% on a total of",len(audio_files),"files")