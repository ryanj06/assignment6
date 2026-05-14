from __future__ import annotations

import re
from calendar import monthrange
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
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
}

WEEKDAYS = {
    "monday": 0,
    "mon": 0,
    "tuesday": 1,
    "tue": 1,
    "tues": 1,
    "wednesday": 2,
    "wed": 2,
    "thursday": 3,
    "thu": 3,
    "thurs": 3,
    "friday": 4,
    "fri": 4,
    "saturday": 5,
    "sat": 5,
    "sunday": 6,
    "sun": 6,
}

NUMBERS = {
    "zero": 0,
    "one": 1,
    "a": 1,
    "an": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = normalize(s)

    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)

    weekday = parse_weekday(text, today)
    if weekday is not None:
        return weekday

    relative = parse_relative(text, today)
    if relative is not None:
        return relative

    absolute = parse_absolute(text, today)
    if absolute is not None:
        return absolute

    raise ValueError(f"Could not parse date: {s}")


def normalize(s: str) -> str:
    text = s.lower().strip()
    text = text.replace(",", "")
    text = text.replace(".", "")
    text = re.sub(r"\b(\d+)(st|nd|rd|th)\b", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text


def parse_num(x: str) -> int:
    if x.isdigit():
        return int(x)
    if x in NUMBERS:
        return NUMBERS[x]
    raise ValueError(f"Invalid number: {x}")


def add_months(d: date, months: int) -> date:
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    day = min(d.day, monthrange(year, month)[1])
    return date(year, month, day)


def add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def apply_amount(base: date, amount: int, unit: str) -> date:
    if unit.startswith("day"):
        return base + timedelta(days=amount)
    if unit.startswith("week"):
        return base + timedelta(weeks=amount)
    if unit.startswith("month"):
        return add_months(base, amount)
    if unit.startswith("year"):
        return add_years(base, amount)
    raise ValueError(f"Invalid unit: {unit}")


def apply_offsets(base: date, text: str, sign: int) -> date:
    parts = re.findall(
        r"\b(\d+|[a-z]+)\s+(day|days|week|weeks|month|months|year|years)\b",
        text,
    )
    if not parts:
        raise ValueError(f"Invalid relative date: {text}")

    result = base
    for num_text, unit in parts:
        result = apply_amount(result, sign * parse_num(num_text), unit)
    return result


def parse_relative(text: str, today: date) -> date | None:
    if text.startswith("in "):
        return apply_offsets(today, text[3:], 1)

    if text.endswith(" ago"):
        return apply_offsets(today, text[:-4], -1)

    match = re.fullmatch(r"(.+) (from|after) (.+)", text)
    if match:
        amount_text, _word, base_text = match.groups()
        return apply_offsets(parse(base_text, today), amount_text, 1)

    match = re.fullmatch(r"(.+) before (.+)", text)
    if match:
        amount_text, base_text = match.groups()
        return apply_offsets(parse(base_text, today), amount_text, -1)

    return None


def parse_weekday(text: str, today: date) -> date | None:
    match = re.fullmatch(r"next ([a-z]+)", text)
    if match and match.group(1) in WEEKDAYS:
        target = WEEKDAYS[match.group(1)]
        days = (target - today.weekday()) % 7
        return today + timedelta(days=days or 7)

    match = re.fullmatch(r"last ([a-z]+)", text)
    if match and match.group(1) in WEEKDAYS:
        target = WEEKDAYS[match.group(1)]
        days = (today.weekday() - target) % 7
        return today - timedelta(days=days or 7)

    if text in WEEKDAYS:
        target = WEEKDAYS[text]
        days = (target - today.weekday()) % 7
        return today + timedelta(days=days)

    return None


def parse_absolute(text: str, today: date) -> date | None:
    match = re.fullmatch(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", text)
    if match:
        y, m, d = map(int, match.groups())
        return date(y, m, d)

    match = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if match:
        m, d, y = map(int, match.groups())
        return date(y, m, d)

    match = re.fullmatch(r"([a-z]+) (\d{1,2}) (\d{4})", text)
    if match and match.group(1) in MONTHS:
        month, day, year = match.groups()
        return date(int(year), MONTHS[month], int(day))

    match = re.fullmatch(r"(\d{1,2}) ([a-z]+) (\d{4})", text)
    if match and match.group(2) in MONTHS:
        day, month, year = match.groups()
        return date(int(year), MONTHS[month], int(day))

    match = re.fullmatch(r"([a-z]+) (\d{1,2})", text)
    if match and match.group(1) in MONTHS:
        month, day = match.groups()
        return date(today.year, MONTHS[month], int(day))

    return None
