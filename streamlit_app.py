import streamlit as st
from datetime import date, timedelta
import calendar
import streamlit as st

def calculate_expiry(period_end, new_proc, late, selfrev, suspend):
    expiry = date(period_end.year, 12, 31) + timedelta(days=5*365)
    if new_proc: expiry += timedelta(days=365)
    if late: expiry += timedelta(days=180)
    if selfrev: expiry += timedelta(days=365)
    if suspend: expiry += timedelta(days=365)
    return expiry

def get_last_day_of_period(year, month, frequency_months):
    start_month = month
    end_month = month + frequency_months - 1
    end_year = year + (end_month - 1) // 12
    end_month = ((end_month - 1) % 12) + 1
    last_day = calendar.monthrange(end_year, end_month)[1]
    return date(end_year, end_month, last_day)

def get_first_non_expired_period(closure_date, frequency, new_proc, late, selfrev, suspend):
    freq_months = {"havi": 1, "negyedéves": 3, "éves": 12}[frequency]
    current = date(closure_date.year, closure_date.month, 1)

    while True:
        period_end = get_last_day_of_period(current.year, current.month, freq_months)
        expiry = calculate_expiry(period_end, new_proc, late, selfrev, suspend)

        if expiry >= closure_date:
            prev_month = current.month - freq_months
            prev_year = current.year
            while prev_month <= 0:
                prev_month += 12
                prev_year -= 1
            current = date(prev_year, prev_month, 1)
        else:
            next_month = current.month + freq_months
            next_year = current.year
            while next_month > 12:
                next_month -= 12
                next_year += 1
            return next_year, next_month

# ---------- Streamlit alkalmazás ----------
st.set_page_config(page_title="ÁFA elévülés kalkulátor", page_icon="📅")
st.title("📅 ÁFA elévülés kalkulátor (Art. 202. § alapján)")

closure_date = st.date_input("📅 Vizsgálat lezárásának dátuma", value=date.today())
frequency = st.selectbox("📊 Bevallás gyakorisága", ["havi", "negyedéves", "éves"])
new_proc = st.checkbox("🚨 Volt új eljárás?")
late = st.checkbox("📤 Késedelmes bevallás?")
selfrev = st.checkbox("📝 Önellenőrzés történt?")
suspend = st.checkbox("⚖️ Volt peres vagy más nyugvásos eljárás?")

if st.button("📌 Számítás indítása"):
    y, m = get_first_non_expired_period(closure_date, frequency, new_proc, late, selfrev, suspend)
    st.success(f"📍 Vizsgálható legkorábbi időszak: {y}. {m:02d}")
