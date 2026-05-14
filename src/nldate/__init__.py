from __future__ import annotations

import re
from datetime import date, timedelta

MONTHS = {
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = s.lower().strip().replace(",", "").replace(".", "")
    text = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", text)

    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)

    if text.startswith("in "):
        match = re.match(r"in (\d+|\w+) days?", text)
        if match:
            n = parse_num(match.group(1))
            return today + timedelta(days=n)

        match = re.match(r"in (\d+|\w+) weeks?", text)
        if match:
            n = parse_num(match.group(1))
            return today + timedelta(weeks=n)

    if text.startswith("next "):
        day = text.split()[1]
        target = WEEKDAYS[day]
        diff = (target - today.weekday()) % 7
        if diff == 0:
            diff = 7
        return today + timedelta(days=diff)

    if "before" in text:
        match = re.match(r"(\d+|\w+) days before (.+)", text)
        if match:
            n = parse_num(match.group(1))
            base = parse(match.group(2), today)
            return base - timedelta(days=n)

    match = re.match(r"([a-z]+) (\d+) (\d{4})", text)
    if match:
        month, day, year = match.groups()
        return date(int(year), MONTHS[month], int(day))

    match = re.match(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if match:
        y, m, d = map(int, match.groups())
        return date(y, m, d)

    match = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match:
        m, d, y = map(int, match.groups())
        return date(y, m, d)

    raise ValueError(f"Could not parse: {s}")


def parse_num(x: str) -> int:
    if x.isdigit():
        return int(x)
    return NUMBER_WORDS[x]
