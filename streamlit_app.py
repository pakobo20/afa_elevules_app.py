import streamlit as st
from datetime import date, timedelta
import calendar
import streamlit as st

def calculate_expiry(due_date, new_proc, late, selfrev, suspend):
    # Alap elévülés: esedékesség évének utolsó napja + 5 év
    expiry = date(due_date.year, 12, 31) + timedelta(days=5*365)
    if new_proc:
        expiry += timedelta(days=365)
    if late:
        expiry += timedelta(days=180)
    if selfrev:
        expiry += timedelta(days=365)
    if suspend:
        expiry += timedelta(days=365)
    return expiry

def get_due_date(period_year, period_month, frequency):
    if frequency == "havi":
        due_month = period_month + 1
        due_year = period_year
        if due_month > 12:
            due_month = 1
            due_year += 1
        return date(due_year, due_month, 20)
    elif frequency == "negyedéves":
        if period_month in [1, 2, 3]:
            return date(period_year, 4, 20)
        elif period_month in [4, 5, 6]:
            return date(period_year, 7, 20)
        elif period_month in [7, 8, 9]:
            return date(period_year, 10, 20)
        elif period_month in [10, 11, 12]:
            return date(period_year + 1, 1, 20)
    elif frequency == "éves":
        return date(period_year + 1, 2, 25)

def get_first_non_expired_period(closure_date, frequency, new_proc, late, selfrev, suspend):
    freq_months = {"havi": 1, "negyedéves": 3, "éves": 12}[frequency]
    current = date(closure_date.year, closure_date.month, 1)

    while True:
        period_month = current.month
        period_year = current.year
        due_date = get_due_date(period_year, period_month, frequency)
        expiry = calculate_expiry(due_date, new_proc, late, selfrev, suspend)

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

# Streamlit alkalmazás
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
