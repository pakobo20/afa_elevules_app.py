import streamlit as st
from datetime import date, timedelta, datetime

def calculate_expiry(period_end, new_proc, late, suspend, selfrev_date=None):
    expiry = date(period_end.year, 12, 31) + timedelta(days=5 * 365)

    if new_proc:
        expiry += timedelta(days=365)
    if late:
        expiry += timedelta(days=180)
    if suspend:
        expiry += timedelta(days=365)

    if selfrev_date:
        expiry = selfrev_date + timedelta(days=5 * 365)

    return expiry

def get_first_non_expired_period(closure_date, frequency, new_proc, late, suspend, selfrev_data):
    freq_months = {"havi": 1, "negyedéves": 3, "éves": 12}[frequency]
    current = date(closure_date.year, closure_date.month, 1)

    while True:
        period_key = (current.year, current.month)
        selfrev_date = selfrev_data.get(period_key)

        expiry = calculate_expiry(current, new_proc, late, suspend, selfrev_date)

        if expiry >= closure_date:
            # még nem évült el, menjünk vissza
            prev_month = current.month - freq_months
            prev_year = current.year
            while prev_month <= 0:
                prev_month += 12
                prev_year -= 1
            current = date(prev_year, prev_month, 1)
        else:
            # ez már elévült, tehát a következő időszak az első nem elévült
            next_month = current.month + freq_months
            next_year = current.year
            while next_month > 12:
                next_month -= 12
                next_year += 1
            return next_year, next_month

# --- Streamlit felület ---
st.set_page_config(page_title="ÁFA Elévülés Kalkulátor", page_icon="📅")
st.title("📅 ÁFA Elévülés Kalkulátor")

closure_date = st.date_input("📅 Vizsgálat lezárásának dátuma", value=date.today())
frequency = st.selectbox("📊 Bevallás gyakorisága", ["havi", "negyedéves", "éves"])

st.markdown("Jelöld be, ha volt ilyen hosszabbító tényező:")
new_proc = st.checkbox("🚨 Volt új eljárás?")
late = st.checkbox("📤 Volt késedelmes bevallás?")
suspend = st.checkbox("⚖️ Volt nyugvás (peres, egyéb eljárás)?")

# Önellenőrzés kezelése
selfrev_data = {}
if st.checkbox("📝 Volt önellenőrzés valamely időszakra?"):
    num_periods = st.number_input("Hány hónapra történt önellenőrzés?", min_value=1, max_value=60, step=1)

    for i in range(num_periods):
        col1, col2 = st.columns(2)
        with col1:
            y = st.number_input(f"{i+1}. év", min_value=2000, max_value=2100, value=2020, key=f"y_{i}")
            m = st.number_input(f"{i+1}. hónap", min_value=1, max_value=12, value=1, key=f"m_{i}")
        with col2:
            d = st.date_input(f"{i+1}. benyújtás dátuma", value=date.today(), key=f"d_{i}")
        selfrev_data[(y, m)] = d

if st.button("📌 Elévülés kiszámítása"):
    y, m = get_first_non_expired_period(closure_date, frequency, new_proc, late, suspend, selfrev_data)
    st.success(f"📍 Vizsgálható legkorábbi időszak: {y}. {m:02d}")
