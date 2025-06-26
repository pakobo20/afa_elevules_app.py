import streamlit as st
from datetime import date, timedelta, datetime

def calculate_expiry(period_end, new_proc, late, selfrev, suspend):
    # Alap elévülés: időszak évének utolsó napja + 5 év
    expiry = date(period_end.year, 12, 31) + timedelta(days=5*365)

    # Hosszabbító tényezők (durva becsléssel 1 év vagy 6 hónap mindegyik)
    if new_proc:
        expiry += timedelta(days=365)
    if late:
        expiry += timedelta(days=180)
    if selfrev:
        expiry += timedelta(days=365)
    if suspend:
        expiry += timedelta(days=365)

    return expiry

def get_first_non_expired_period(closure_date, frequency, new_proc, late, selfrev, suspend):
    today = closure_date
    freq_months = {"havi": 1, "negyedéves": 3, "éves": 12}[frequency]

    # kezdjük a vizsgálat hónapjától visszafelé keresni
    current = date(today.year, today.month, 1)

    while True:
        period_end = current.replace(day=1)
        expiry = calculate_expiry(period_end, new_proc, late, selfrev, suspend)

        if expiry >= today:
            # ha még nem évült el, menjünk eggyel visszább
            prev_month = current.month - freq_months
            prev_year = current.year
            while prev_month <= 0:
                prev_month += 12
                prev_year -= 1
            current = date(prev_year, prev_month, 1)
        else:
            # ha elévült, akkor az utána következő az első vizsgálható
            next_month = current.month + freq_months
            next_year = current.year
            while next_month > 12:
                next_month -= 12
                next_year += 1
            return next_year, next_month

# Streamlit app
st.set_page_config(page_title="ÁFA elévülés kalkulátor", page_icon="📅")
st.title("📅 ÁFA elévülés kalkulátor (Art. 202. § alapján)")

closure_date = st.date_input("📅 Vizsgálat lezárásának dátuma", value=date.today())
frequency = st.selectbox("📊 Bevallás gyakorisága", ["havi", "negyedéves", "éves"])

st.markdown("Jelöld be azokat a körülményeket, amelyek hosszabbíthatják az elévülést:")

new_proc = st.checkbox("🚨 Volt új eljárás?")
late = st.checkbox("📤 Késedelmes bevallás?")
selfrev = st.checkbox("📝 Önellenőrzés történt?")
suspend = st.checkbox("⚖️ Volt peres vagy más nyugvásos eljárás?")

if st.button("📌 Számítás indítása"):
    y, m = get_first_non_expired_period(closure_date, frequency, new_proc, late, selfrev, suspend)
    st.success(f"📍 Vizsgálható legkorábbi időszak: {y}. {m:02d}")
