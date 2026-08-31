import base64
import datetime
import glob
import json
import os
import pandas as pd
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Πωλήσεις ανά Κατάστημα", layout="centered")

st.markdown(
    """
    <style>
    .stApp { background-color: #2c3e50 !important; }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    div[data-baseweb="select"] > div, .stRadio label p { color: white !important; }
    .block-container { padding: 0rem 0.5rem !important; max-width: 100% !important; }
    </style>
""",
    unsafe_allow_html=True,
)

excel_path = "tv_sat_sales.xlsx"
time_path = "upload_time.txt"
confetti_path = "confetti_status.txt"
cheer_path = "cheer_status.txt"
redirect_url = "https://split-sales-spame-tis-times-tomeas3.streamlit.app/"


def upload_to_github(
    file_path, repo_name, token, commit_message="Update sales file"
):
  if not token or not repo_name:
    return False
  try:
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    r = requests.get(url, headers=headers)
    sha = None
    if r.status_code == 200:
      sha = r.json().get("sha")

    with open(file_path, "rb") as f:
      content_bytes = f.read()
    content_encoded = base64.b64encode(content_bytes).decode("utf-8")

    data = {"message": commit_message, "content": content_encoded}
    if sha:
      data["sha"] = sha

    put_r = requests.put(url, headers=headers, data=json.dumps(data))
    return put_r.status_code in [200, 201]
  except Exception:
    return False


confetti_enabled = True
if os.path.exists(confetti_path):
  try:
    with open(confetti_path, "r", encoding="utf-8") as cf:
      confetti_enabled = cf.read().strip() == "True"
  except Exception:
    pass

cheer_enabled = True
if os.path.exists(cheer_path):
  try:
    with open(cheer_path, "r", encoding="utf-8") as ch:
      cheer_enabled = ch.read().strip() == "True"
  except Exception:
    pass

with st.expander("⚙️ Διαχείριση Αρχείου (Admin)"):
  password = st.text_input("Εισάγετε κωδικό διαχειριστή:", type="password")
  if password == "2845":
    uploaded_file = st.file_uploader(
        "Σύρετε το νέο αρχείο πωλήσεων εδώ:", type=["xlsx"]
    )

    time_options = []
    for hour in range(8, 23):
      for minute in (0, 30):
        time_options.append(datetime.time(hour, minute))
    time_options.append(datetime.time(22, 0))
    time_options = sorted(list(set(time_options)))

    now = datetime.datetime.now() - datetime.timedelta(hours=1)
    default_minute = 0 if now.minute < 30 else 30
    default_hour = max(8, min(22, now.hour))
    default_time = datetime.time(default_hour, default_minute)

    if "selected_half_hour" not in st.session_state:
      st.session_state.selected_half_hour = default_time

    col_time, col_confetti, col_cheer = st.columns([1.2, 1, 1])

    with col_time:
      selected_time = st.selectbox(
          "Ώρα αναφοράς:",
          options=time_options,
          index=(
              time_options.index(st.session_state.selected_half_hour)
              if st.session_state.selected_half_hour in time_options
              else 0
          ),
          format_func=lambda x: x.strftime("%H:%M"),
      )
      st.session_state.selected_half_hour = selected_time

    with col_confetti:
      confetti_choice = st.radio(
          "Κομφετί:", ["ΝΑΙ", "ΟΧΙ"], index=0 if confetti_enabled else 1, horizontal=True
      )

    with col_cheer:
      cheer_choice = st.radio(
          "Χειροκρότημα:",
          ["ΝΑΙ", "ΟΧΙ"],
          index=0 if cheer_enabled else 1,
          horizontal=True,
      )

    if uploaded_file is not None:
      file_bytes = uploaded_file.getbuffer()
      with open(excel_path, "wb") as f:
        f.write(file_bytes)

      current_time_str = selected_time.strftime("%H:%M")
      with open(time_path, "w", encoding="utf-8") as tf:
        tf.write(current_time_str)

      with open(confetti_path, "w", encoding="utf-8") as cf:
        cf.write(str(confetti_choice == "ΝΑΙ"))

      with open(cheer_path, "w", encoding="utf-8") as ch:
        ch.write(str(cheer_choice == "ΝΑΙ"))

      try:
        gh_token = st.secrets["GITHUB_TOKEN"]
        repo_name = st.secrets["REPO_NAME"]
        upload_to_github(
            excel_path, repo_name, gh_token, "Auto-update tv_sat_sales.xlsx"
        )
        upload_to_github(time_path, repo_name, gh_token, "Auto-update upload time")
      except Exception:
        pass

      st.success("Το αρχείο μετονομάστηκε και συγχρονίστηκε επιτυχώς!")
      components.html(
          """
                <script>
                    setTimeout(function() {
                        window.parent.location.reload();
                    }, 1000);
                </script>
            """,
          height=0,
      )
  elif password:
    st.error("Λάθος κωδικός!")


def load_data():
  if os.path.exists(excel_path):
    try:
      df = pd.read_excel(excel_path, header=None)
      return df
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
  elif
