import base64
import glob
import os
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Πωλήσεις ανά Κατάστημα", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background-color: #2c3e50 !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .block-container { padding: 0rem 0.5rem !important; max-width: 100% !important; }
    
    @keyframes pulse-glow {
        0% {
            transform: scale(1);
            box-shadow: 0 0 10px rgba(39, 174, 96, 0.4), 0 6px 15px rgba(39, 174, 96, 0.4);
            border-color: rgba(255, 255, 255, 0.2);
        }
        50% {
            transform: scale(1.03);
            box-shadow: 0 0 25px rgba(46, 204, 113, 0.9), 0 0 40px rgba(39, 174, 96, 0.6);
            border-color: rgba(255, 255, 255, 0.9);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 10px rgba(39, 174, 96, 0.4), 0 6px 15px rgba(39, 174, 96, 0.4);
            border-color: rgba(255, 255, 255, 0.2);
        }
    }

    @keyframes pointing-down {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-8px) scale(1.15); }
        100% { transform: translateY(0px) scale(1); }
    }

    .pointing-hand {
        display: block;
        text-align: center;
        font-size: 32px;
        margin-bottom: 8px;
        animation: pointing-down 1s infinite ease-in-out;
        user-select: none;
        filter: drop-shadow(0 2px 5px rgba(0,0,0,0.6));
    }
    
    .redirect-btn {
        display: block;
        width: 100%;
        max-width: 450px;
        margin: 20px auto;
        box-sizing: border-box;
        background: linear-gradient(135deg, #27ae60, #219653);
        color: white !important;
        padding: 16px 20px;
        border-radius: 14px;
        text-decoration: none;
        text-align: center;
        font-size: 17px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        border: 2px solid rgba(255, 255, 255, 0.2);
        animation: pulse-glow 1.8s infinite ease-in-out;
    }
    
    .redirect-btn:hover {
        background: linear-gradient(135deg, #219653, #1e8449);
        color: white !important;
    }

    .banner-img {
        width: 100%;
        height: auto;
        display: block;
        border-radius: 0;
        margin: 0;
        padding: 0;
        cursor: pointer;
    }
    </style>
""",
    unsafe_allow_html=True,
)

excel_path = "tv_sat_sales.xlsx"
time_path = "upload_time.txt"
target_url = "https://upload-tv-spame-tosoun.streamlit.app/"

confetti_enabled = True
cheer_enabled = True


def load_data():
    if os.path.exists(excel_path):
        try:
            return pd.read_excel(excel_path, header=None)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def clean_quantity_value(val):
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s_val = str(val).strip()
    if "," in s_val and "." in s_val:
        s_val = s_val.replace(".", "").replace(",", ".")
    elif "," in s_val:
        s_val = s_val.replace(",", ".")
    try:
        return float(s_val)
    except Exception:
        return 0.0


def format_smart_num(num):
    if num == int(num):
        return f"{int(num):,}".replace(",", ".")
    else:
        parts = f"{num:.3f}".split(".")
        int_part = int(parts[0])
        dec_part = parts[1].rstrip("0")
        formatted_int = f"{int_part:,}".replace(",", ".")
        return f"{formatted_int},{dec_part}"


try:
    df = load_data()
    custom_title = "ΕΙΔΟΣ"

    if not df.empty:
        for i in range(min(5, len(df))):
            for j in range(len(df.columns)):
                val = str(df.iloc[i, j]).strip()
                if (
                    val
                    and val.lower() != "nan"
                    and ("κατάστημα" not in val.lower())
                    and ("πληρωτ" not in val.lower())
                    and ("ποσοτ" not in val.lower())
                    and ("αξια" not in val.lower())
                    and ("κοστος" not in val.lower())
                ):
                    custom_title = val
                    break
            if custom_title != "ΕΙΔΟΣ":
                break

        header_row_idx = 0
        for i in range(min(5, len(df))):
            row_str = str(df.iloc[i].values).lower()
            if "κατάστημα" in row_str or "καταστημα" in row_str:
                header_row_idx = i
                break

        df = df.iloc[header_row_idx + 1 :].reset_index(drop=True)

        if len(df.columns) >= 3:
            df = df.iloc[:, [0, 2]]
        elif len(df.columns) >= 2:
            df = df.iloc[:, [0, 1]]
        else:
            df = df.iloc[:, [0, 0]]

        df.columns = ["Κατάστημα", "Ποσότητα"]
        df = df.dropna(subset=["Κατάστημα", "Ποσότητα"])
        df["Κατάστημα"] = df["Κατάστημα"].astype(str).str.strip()

        df = df[
            ~df["Κατάστημα"].str.contains(
                "Κατάστημα|ΠΟΣΟΤ|ΠΑΡΑΔΕΙΓΜΑ|NaN", case=False, na=False
            )
        ]
        df_clean = df[
            ~df["Κατάστημα"].str.contains("Total|Συνολο|ΣΥΝΟΛΟ", case=False, na=False)
        ].copy()

        df_clean["Num_Sales"] = df_clean["Ποσότητα"].apply(clean_quantity_value)

        df_stores = (
            df_clean.sort_values(by="Num_Sales", ascending=False)
            .reset_index(drop=True)
        )
        total_sum = df_stores["Num_Sales"].sum()
        max_sales = df_stores["Num_Sales"].max() if not df_stores.empty else 1.0
    else:
        df_stores = pd.DataFrame()
        total_sum = 0.0
        max_sales = 1.0

    img_src = ""
    banner_files = (
        glob.glob("ChatGPT Image*.png")
        + glob.glob("*banner*.jpg")
        + glob.glob("*banner*.png")
    )
    if banner_files:
        banner_filename = banner_files[0]
        with open(banner_filename, "rb") as image_file:
            img_src = (
                f"data:image/png;base64,{base64.b64encode(image_file.read()).decode()}"
            )

    # 1. Clickable Banner με target="_blank" (νεα καρτέλα)
    if img_src:
        st.markdown(
            f'<a href="{target_url}" target="_blank"><img src="{img_src}" class="banner-img" alt="banner"></a>',
            unsafe_allow_html=True,
        )

    # 2. Clickable Button με target="_blank" (νεα καρτέλα)
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 20px;">
            <div class="pointing-hand">👇</div>
            <a href="{target_url}" target="_blank" class="redirect-btn">🔗 ΜΕΤΑΒΑΣΗ ΣΤΟΝ ΤΟΜΕΑ 3</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3. Περιεχόμενο λίστας (στατιστικά, μπάρες προόδου, confetti)
    html_parts = [
        """
        <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800&display=swap" rel="stylesheet">
        
        <style>
        @keyframes blink-number-slow {
            0% { opacity: 1; color: #2ecc71; text-shadow: 0 0 12px rgba(46, 204, 113, 0.7); }
            50% { opacity: 0.25; color: #27ae60; text-shadow: none; }
            100% { opacity: 1; color: #2ecc71; text-shadow: 0 0 12px rgba(46, 204, 113, 0.7); }
        }

        body { font-family: 'Montserrat', sans-serif; margin: 0; padding: 0; background: transparent; width: 100%; overflow-x: hidden; }
        .main-container { 
            position: relative;
            background: rgba(0, 0, 0, 0.6); 
            padding: 15px; 
            border-radius: 0; 
            box-shadow: none; 
            backdrop-filter: blur(8px); 
            -webkit-backdrop-filter: blur(8px); 
            width: 100%; 
            max-width: 100%; 
            margin: 0 auto; 
            text-align: center; 
            overflow: hidden;
        }
        .sub-title { color: #3498db; font-size: 18px; margin-bottom: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
        .poll-item { background: rgba(255, 255, 255, 0.08); padding: 12px 18px; border-radius: 12px; margin-bottom: 12px; text-align: left; border: 1px solid rgba(255, 255, 255, 0.1); }
        .poll-info { display: flex; justify-content: space-between; align-items: flex-start; color: white; font-size: 15px; font-weight: 600; margin-bottom: 8px; gap: 10px; }
        .poll-info span:first-child { word-break: break-word; overflow-wrap: break-word; flex: 1; }
        .poll-info span:last-child { white-space: nowrap; text-align: right; flex-shrink: 0; }
        .win-number-first { color: #2ecc71; animation: blink-number-slow 2.5s infinite ease-in-out; font-weight: 700; }
        .progress-bar-bg { background: rgba(255, 255, 255, 0.15); border-radius: 10px; height: 12px; width: 100%; overflow: hidden; }
        .progress-fill { background: #3498db; height: 100%; border-radius: 10px; }
        .total-item { background: rgba(52, 152, 219, 0.25); border: 1px solid #3498db; }
        .watermark { text-align: right; color: rgba(255, 255, 255, 0.2); font-size: 10px; letter-spacing: 1px; margin-top: 15px; margin-right: 5px; text-transform: uppercase; user-select: none; }
        </style>
        
        <div class="main-container">
            <audio id="cheerAudio" preload="auto">
                <source src="https://www.myinstants.com/media/sounds/applause.mp3" type="audio/mpeg">
            </audio>
    """,
    ]

    if not df_stores.empty:
        html_parts.append(
            '<div class="sub-title">' + str(custom_title) + "</div>"
        )
        for index, row in df_stores.iterrows():
            katastima = str(row["Κατάστημα"])
            if katastima.lower() == "nan" or not katastima.strip():
                continue
            num = row["Num_Sales"]
            formatted_num = format_smart_num(num)
            bar_width = round((num / max_sales) * 100) if max_sales > 0 else 0
            if bar_width > 100:
                bar_width = 100

            if index == 0:
                html_parts.append(
                    '<div class="poll-item" id="first-store-card">'
                    + '<div class="poll-info">'
                    + "<span><b>"
                    + katastima
                    + "</b></span>"
                    + '<span class="win-number-first">'
                    + formatted_num
                    + " τμχ/κιλ</span>"
                    + "</div>"
                    + '<div class="progress-bar-bg"><div class="progress-fill" style="width: '
                    + str(bar_width)
                    + '%;"></div></div>'
                    + "</div>"
                )
                if confetti_enabled:
                    html_parts.append(
                        """
                        <script>
                            setTimeout(function() {
                                const card = document.getElementById('first-store-card');
                                if(card) {
                                    const rect = card.getBoundingClientRect();
                                    const x = (rect.left + rect.width / 2) / window.innerWidth;
                                    const y = (rect.top + rect.height / 2) / window.innerHeight;
                                    confetti({ particleCount: 100, spread: 80, origin: { x: x, y: y } });
                                }
                            }, 300);
                        </script>
                        """
                    )
                if cheer_enabled:
                    html_parts.append(
                        """
                        <script>
                            document.addEventListener("DOMContentLoaded", function() {
                                const audio = document.getElementById('cheerAudio');
                                if(audio) {
                                    audio.volume = 0.5;
                                    audio.play().catch(function() {});
                                }
                            });
                        </script>
                        """
                    )
            else:
                html_parts.append(
                    '<div class="poll-item">'
                    + '<div class="poll-info">'
                    + "<span><b>"
                    + katastima
                    + "</b></span>"
                    + "<span><b>"
                    + formatted_num
                    + " τμχ/κιλ</b></span>"
                    + "</div>"
                    + '<div class="progress-bar-bg"><div class="progress-fill" style="width: '
                    + str(bar_width)
                    + '%;"></div></div>'
                    + "</div>"
                )

        formatted_total = format_smart_num(total_sum)
        html_parts.append(
            '<div class="poll-item total-item">'
            + '<div class="poll-info">'
            + "<span><b>TOTAL</b></span>"
            + "<span><b>"
            + formatted_total
            + " τμχ/κιλ</b></span>"
            + "</div>"
            + '<div class="progress-bar-bg"><div class="progress-fill" style="width: 100%;"></div></div>'
            + "</div>"
        )

    html_parts.append('<div class="watermark">tosoun 2026</div></div>')
    final_html = "".join(html_parts)
    components.html(final_html, height=1100, scrolling=True)

except Exception as e:
    st.error(f"Σφάλμα: {e}")
