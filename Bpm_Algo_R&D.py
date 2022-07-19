import array
import math
import wave
from glob import glob
import matplotlib.pyplot as plt
import numpy
import pywt
import pandas as pd
from scipy import signal

def read_wav(filename):
    # open file, get metadata for audio
    try:
        wf = wave.open(filename, "rb")
    except IOError as e:
        print(e)
        return

    # typ = choose_type( wf.getsampwidth() ) # TODO: implement choose_type
    nsamps = wf.getnframes()
    assert nsamps > 0
    fs = wf.getframerate()
    assert fs > 0
    # Read entire file and make into an array
    samps = list(array.array("i", wf.readframes(nsamps)))
    try:
        assert nsamps == len(samps)
    except AssertionError:
        print(nsamps, "not equal to", len(samps))
    return samps, fs

# print an error when no data can be found
def no_audio_data():
    print("No audio data for sample, skipping...")
    return None, None

# simple peak detection
def peak_detect(data):
    max_val = numpy.amax(abs(data))
    peak_ndx = numpy.where(data == max_val)
    if len(peak_ndx[0]) == 0:  # if nothing found then the max must be negative
        peak_ndx = numpy.where(data == -max_val)
    return peak_ndx

def bpm_detector(data, fs):
    cA = []
    cD = []
    correl = []
    cD_sum = []
    levels = 4
    max_decimation = 2 ** (levels - 1)
    min_ndx = math.floor(60.0 / 220 * (fs / max_decimation))
    max_ndx = math.floor(60.0 / 40 * (fs / max_decimation))
    for loop in range(0, levels):
        cD = []
        # 1) DWT
        if loop == 0:
            [cA, cD] = pywt.dwt(data, "db4")
            cD_minlen = len(cD) / max_decimation + 1
            cD_sum = numpy.zeros(math.floor(cD_minlen))
        else:
            [cA, cD] = pywt.dwt(cA, "db4")
        # 2) Filter
        cD = signal.lfilter([0.01], [1 - 0.99], cD)
        # 4) Subtract out the mean.
        # 5) Decimate for reconstruction later.
        cD = abs(cD[:: (2 ** (levels - loop - 1))])
        cD = cD - numpy.mean(cD)
        # 6) Recombine the signal before ACF
        #    Essentially, each level the detail coefs (i.e. the HPF values) are concatenated to the beginning of the array
        cD_sum = cD[0 : math.floor(cD_minlen)] + cD_sum
    if [b for b in cA if b != 0.0] == []:
        return no_audio_data()
    # Adding in the approximate data as well...
    cA = signal.lfilter([0.01], [1 - 0.99], cA)
    cA = abs(cA)
    cA = cA - numpy.mean(cA)
    cD_sum = cA[0 : math.floor(cD_minlen)] + cD_sum
    # ACF
    correl = numpy.correlate(cD_sum, cD_sum, "full")
    midpoint = math.floor(len(correl) / 2)
    correl_midpoint_tmp = correl[midpoint:]
    peak_ndx = peak_detect(correl_midpoint_tmp[min_ndx:max_ndx])
    if len(peak_ndx) > 1:
        return no_audio_data()
    peak_ndx_adjusted = peak_ndx[0] + min_ndx
    bpm = 60.0 / peak_ndx_adjusted * (fs / max_decimation)
    print(bpm)
    return bpm, correl

if __name__ == "__main__":
    arr = []
    filename_arr = []
    value = []
    count = 0
    window=3.0
    data_dir = 'D:/Python programing ide/dataset'
    audio_files = glob(data_dir + '/*.wav')
    for i in range(0, len(audio_files), 1):
        filename_arr.append(audio_files[i])
    for i in range(0, len(audio_files), 1):
        samps, fs =read_wav(audio_files[i])
        print(audio_files[i])
        data = []
        correl = []
        bpm = 0
        n = 0
        nsamps = len(samps)
        window_samps = int(window * fs)
        samps_ndx = 0  # First sample in window_ndx
        max_window_ndx = math.floor(nsamps / window_samps)
        bpms = numpy.zeros(max_window_ndx)
        for window_ndx in range(0, max_window_ndx):
            data = samps[samps_ndx : samps_ndx + window_samps]
            if not ((len(data) % window_samps) == 0):
                raise AssertionError(str(len(data)))

            bpm, correl_temp = bpm_detector(data, fs)
            if bpm is None:
                continue
            bpms[window_ndx] = bpm
            correl = correl_temp
            samps_ndx = samps_ndx + window_samps
            n = n + 1
        bpm = numpy.median(bpms)
        arr.append(bpm)
        print("Completed!  Estimated Beats Per Minute:", bpm)
        n = range(0, len(correl))
        plt.plot(n, abs(correl))
        plt.show(block=False)
        plt.pause(3)
        plt.close()

    df = pd.DataFrame({'File Names': filename_arr, 'Tempo detection using librosa ': arr})
    writer = pd.ExcelWriter('BPM_detector_algo.xlsx', engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    writer.save()

    f1 = pd.read_excel("BPM_detector_algo.xlsx")
    f2 = pd.read_excel("D:/Python programing ide/result.xlsx")

    f3 = f1.merge(f2, left_on=None, right_on=None, left_index=False, right_index=False)

    f3.to_excel("BPM_detector_algo_final.xlsx", index=False)
    xl = pd.ExcelFile('BPM_detector_algo_final.xlsx')
    get_sheet = xl.parse('Sheet1')
    for j in range(0, len(audio_files), 1):
        get_var = get_sheet['RESULT'][j]
        value.append(get_var)

    for j in range(0, len(audio_files), 1):
        a = arr[j]
        b = value[j]
        upper_bound = b + b * 0.02
        lower_bound = b - b * 0.02
        if (a > lower_bound and a < upper_bound):
            count = count + 1
    result = (count / (len(audio_files))) * 100
    print("So the precission of BPM detector algorithm is", result, "% on a total of", len(audio_files), "files")
