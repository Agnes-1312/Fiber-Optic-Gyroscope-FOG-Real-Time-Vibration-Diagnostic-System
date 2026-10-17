import numpy as np
def remove_dc_offset(signal):
    mean_dc=np.mean(signal)
    corrected_signal=signal-mean_dc
    return corrected_signal,mean_dc
def calculate_rms(signal):
    rms_value=np.sqrt(np.mean(np.square(signal)))
    return rms_value
def calculate_fft(signal,fs=10000):
    N=len(signal)
    fft_values=np.fft.fft(signal)
    fft_freq=np.fft.fftfreq(N,d=1.0/fs)
    positive_freq=fft_freq[:N//2]
    amplitude=(2.0/N)*np.abs(fft_values[:N//2])
    return positive_freq,amplitude
def classify_iso10816(v_rms,machine_class="Class I(Precision Instruments)"):
    thresholds={"Class I (Precision Instruments)":(0.28,0.71,1.80),"Class II (Medium Machines)":(0.71,1.80,4.50),"Class III (Large Rigid Foundation)":(1.40,2.80,4.50),"class IV (Large Flexible Foundation)":(2.30,4.50,7.10)}
    th_a,th_b,th_c=thresholds.get(machine_class,(0.28,0.71,1.80))
    if v_rms<th_a:
        return "Zone A(Good)","#28a745","Good Condition: Newly commissioned or recently serviced machinery."
    elif v_rms<th_b:
        return "Zone B(Satisfactory)","#17a2b8","Satisfactory condintion: Acceptable for unrestricted long-term operation."
    elif v_rms <th_b:
        return "Zone C(Unsatisfactory)","#ffc107","Unsatisfactory condition: High vibration; unisuitable for continous long-term operation."
    else:
        return "Zone D(Unacceptable)","#dc3545","Unacceptable condintion: Servere vibration; risk of immediate structural damage!" 
def find_top_peaks(freq, amplitude, top_n=3):
    shorted_indices=np.argsort(amplitude)[::-1]
    top_freqs=freq[shorted_indices[:top_n]]
    top_ams=amplitude[shorted_indices[:top_n]]
    return top_freqs,top_ams
def filter_invalid_data(signal,min_val=-10000,max_val=10000):
    valid_mask=(signal>min_val)&(signal<max_val)
    cleaned_signal=signal[valid_mask]
    return cleaned_signal
