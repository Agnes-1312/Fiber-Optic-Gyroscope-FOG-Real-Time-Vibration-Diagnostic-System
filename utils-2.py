import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import utils

# 頁面標題與寬度設定
st.set_page_config(page_title="FOG Vibration Diagnostic System", layout="wide")

st.title("🔍 Fiber Optic Gyroscope (FOG) Real-Time Vibration Diagnostic System")
st.caption("Engineering B: Real-Time Vibration Diagnostics & ISO 10816 Standard Evaluation")

# 側邊欄設定 (Sidebar Settings)
st.sidebar.header("⚙️ Data Import & Settings")
uploaded_file = st.sidebar.file_uploader("Upload FOG Experimental Data (.xlsx / .csv)", type=["xlsx", "csv"])
sampling_rate = st.sidebar.number_input("Sampling Rate (Hz)", value=10000, step=1000)

# 💡 新增：機台類別選擇 (Machine Class Selector)
machine_class = st.sidebar.selectbox(
    "Select ISO 10816 Machine Class",
    [
        "Class I (Precision Instruments)",
        "Class II (Medium Machines)",
        "Class III (Large Rigid Foundation)",
        "Class IV (Large Flexible Foundation)"
    ],
    index=0  # 預設為 Class I 小型精密儀器
)

if uploaded_file is not None:
    # 讀取檔案 (CSV 或 Excel)
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.sidebar.success(f"Successfully Loaded: {uploaded_file.name}")

    # 選擇訊號欄位
    selected_col = st.sidebar.selectbox("Select Vibration Signal Column", df.columns)

    # 清除 Excel 尾端空白/NaN，100% 保留所有真實數字
    raw_signal = pd.to_numeric(df[selected_col], errors='coerce').dropna().values

    if len(raw_signal) > 0:
        # 核心 DSP 演算法 (傳入選擇的機台類別)
        corrected_signal, mean_dc = utils.remove_dc_offset(raw_signal)
        v_rms = utils.calculate_rms(corrected_signal)
        freq, amp = utils.calculate_fft(corrected_signal, fs=sampling_rate)
        top_freqs, top_amps = utils.find_top_peaks(freq, amp)

        dom_freq = top_freqs[0] if len(top_freqs) > 0 else 0.0
        peak_amp = top_amps[0] if len(top_amps) > 0 else 0.0
        
        # 依據選擇的類別動態計算 Zone A~D 門檻
        status, color, desc = utils.classify_iso10816(v_rms, machine_class=machine_class)

        # ---------------------------------------------------------
        # 第一區塊：Executive Summary & Health Diagnostics
        # ---------------------------------------------------------
        st.subheader("📌 Executive Summary & Health Diagnostics")
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown(
                f"""
                <div style="background-color: {color}; padding: 20px; border-radius: 10px; color: white;">
                    <h2 style="color: white; margin:0;">{status}</h2>
                    <p style="margin-top: 10px; color: white;">{desc}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.metric("RMS Velocity", f"{v_rms:.3f} mm/s")
            st.caption(f"DC Offset Corrected: {mean_dc:.4f}")

        with col3:
            st.metric("Dominant Frequency", f"{dom_freq:.1f} Hz")
            st.caption(f"Peak Amplitude: {peak_amp:.4f}")

        st.markdown("---")

        # ---------------------------------------------------------
        # 第二區塊：Core Engineering Signal Analysis
        # ---------------------------------------------------------
        st.subheader("📌 Core Engineering Signal Analysis")
        col_fig1, col_fig2 = st.columns(2)

        display_points = min(len(corrected_signal), 2000)

        with col_fig1:
            fig_time = px.line(
                x=list(range(display_points)),
                y=corrected_signal[:display_points],
                labels={'x': f'Sample Index (Total: {len(corrected_signal)} points)', 'y': 'Amplitude'},
                title=f"Figure A: Time-Domain Waveform (Showing {display_points} points)"
            )
            st.plotly_chart(fig_time, use_container_width=True)

        with col_fig2:
            fig_fft = px.line(
                x=freq,
                y=amp,
                labels={'x': 'Frequency (Hz)', 'y': 'Magnitude'},
                title="Figure B: FFT Frequency Spectrum"
            )
            fig_fft.update_traces(line_color='red')
            st.plotly_chart(fig_fft, use_container_width=True)

        st.markdown("---")

        # ---------------------------------------------------------
        # 第三區塊：Standards Reference & Raw Data (上下垂直全寬)
        # ---------------------------------------------------------
        st.subheader("📌 Standards Reference & Raw Data")

        # 上層：全類別 ISO 10816 門檻對照表
        with st.expander("📖 View Complete ISO 10816-3 Threshold Criteria (All Machine Classes)"):
            st.markdown(f"**Currently Selected Target:** `{machine_class}`")
            st.markdown("""
            | Machine Class | Zone A (Good) | Zone B (Satisfactory) | Zone C (Unsatisfactory) | Zone D (Unacceptable) |
            | :--- | :--- | :--- | :--- | :--- |
            | **Class I (Precision Instruments)** | `< 0.28 mm/s` | `0.28 - 0.71 mm/s` | `0.71 - 1.80 mm/s` | `> 1.80 mm/s` |
            | **Class II (Medium Machines)** | `< 0.71 mm/s` | `0.71 - 1.80 mm/s` | `1.80 - 4.50 mm/s` | `> 4.50 mm/s` |
            | **Class III (Large Rigid Foundation)** | `< 1.40 mm/s` | `1.40 - 2.80 mm/s` | `2.80 - 4.50 mm/s` | `> 4.50 mm/s` |
            | **Class IV (Large Flexible Foundation)** | `< 2.30 mm/s` | `2.30 - 4.50 mm/s` | `4.50 - 7.10 mm/s` | `> 7.10 mm/s` |
            """)

        # 下層：原始實驗數據表格（享有完整全寬）
        with st.expander("📊 View Uploaded Raw Dataset"):
            st.dataframe(df, use_container_width=True)

    else:
        st.error("⚠️ 所選欄位中沒有有效的數值資料，請重新選擇欄位。")
else:
    st.info("👈 Please upload an Excel/CSV file from the sidebar to start analysis.")