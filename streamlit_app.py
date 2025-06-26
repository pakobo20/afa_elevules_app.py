import streamlit as st
from datetime import date, timedelta

def calc_last_non_expired_period(today: date, freq, flags):
    """
    today: vizsgálat lezárásának várható dátuma
    freq: "havi", "negyedes", "eves"
    flags: dict kulcsokkal:
        late_filing, new_procedure, self_rev_favor, litigation, self_rev_date, litig_start, litig_end
    """

    periods = []

    if freq == "havi":
        periods = [(d.year, d.month) for d in
                   (date(today.year - y, m, 1)
                    for y in range(0,6) for m in range(1,13))]
    elif freq == "negyedes":
        months = [1,4,7,10]
        periods = [(y, q) for y in range(today.year-6, today.year+1) for q in months]
    elif freq == "eves":
        periods = [(y, 12) for y in range(today.year-6, today.year+1)]
    else:
        raise ValueError

    non_expired = []
    for y, m in periods:
        period_end = date(y, m, 1)
        # per last day of period:
        if freq == "havi":
            next_month = m % 12 + 1
            next_year = y + (1 if next_month ==1 else 0)
            period_end = date(next_year, next_month, 1) - timedelta(days=1)
        else:
            period_end = date(y, m, 1) + timedelta(days=31)
            period_end = period_end.replace(day=1) - timedelta(days=1)

        expiry = date(period_end.year, 12, 31) + timedelta(days=5*365)

        # késedelmes bevallás esetén
        if flags['late_filing']:
            rem = (expiry - today).days
            if rem < 183:
                expiry += timedelta(days=183)

        # új eljárás
        if flags['new_procedure']:
            expiry += timedelta(days=365)

        # önellenőrzés az adózó javára
        if flags['self_rev_favor']:
            # új 5 év a önrev évének 12.31-től
            sr_date = flags.get('self_rev_date') or today
            expiry = date(sr_date.year, 12, 31) + timedelta(days=5*365)

        # peres eljárás esetén: nyugvás
        if flags['litigation']:
            # ha folyamatban, várjuk be a végeredményt
            litig_end = flags.get('litig_end')
            if litig_end and today < litig_end:
                expiry += (litig_end - today)  # nem számít bele
            # lezárástól + végrehajthatóság?

        if expiry >= today:
            non_expired.append((y, m, expiry))

    if not non_expired:
        return None

    # a legkisebb időszak még nem elévült
    non_expired.sort()
    return non_expired[0][:2]
