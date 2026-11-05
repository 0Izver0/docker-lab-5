import os
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

# Фіксовані курси: скільки гривень коштує 1 одиниця валюти.
RATES_TO_UAH = {
    "USD": Decimal("41.50"),
    "EUR": Decimal("45.20"),
    "UAH": Decimal("1"),
    "GBP": Decimal("53.80"),
}
CURRENCIES = tuple(RATES_TO_UAH)

CENT = Decimal("0.01")
RATE_PRECISION = Decimal("0.0001")
DEFAULTS = {"AMOUNT": "100", "FROM": "USD", "TO": "EUR"}


def parse_amount(raw):
    text = str(raw).strip().replace(",", ".")
    try:
        amount = Decimal(text)
    except InvalidOperation:
        raise ValueError(f"сума «{raw}» не є числом") from None
    if not amount.is_finite():
        raise ValueError(f"сума «{raw}» має бути скінченним числом")
    if amount <= 0:
        raise ValueError("сума має бути додатною")
    return amount


def normalize_currency(code):
    normalized = str(code).strip().upper()
    if normalized not in RATES_TO_UAH:
        supported = ", ".join(CURRENCIES)
        raise ValueError(f"валюта «{code}» не підтримується (доступні: {supported})")
    return normalized


def round_money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def convert(amount, source, target):
    uah = amount * RATES_TO_UAH[source]
    return round_money(uah / RATES_TO_UAH[target])


def cross_rate(source, target):
    rate = RATES_TO_UAH[source] / RATES_TO_UAH[target]
    return rate.quantize(RATE_PRECISION, rounding=ROUND_HALF_UP)


def fmt_money(value):
    return f"{value:,.2f}".replace(",", " ")


def format_rates_table():
    head = "  з \\ в |" + "".join(f" {c:>9} |" for c in CURRENCIES)
    line = "-" * len(head)
    rows = [head, line]
    for src in CURRENCIES:
        cells = "".join(f" {cross_rate(src, dst):>9} |" for dst in CURRENCIES)
        rows.append(f"  {src:>5} |{cells}")
    return "\n".join(rows)


def format_details(amount, source, target):
    uah = amount * RATES_TO_UAH[source]
    result = convert(amount, source, target)
    return "\n".join(
        [
            f"  Сума:       {fmt_money(round_money(amount))} {source}",
            f"  Курс:       1 {source} = {RATES_TO_UAH[source]} UAH;"
            f" 1 {target} = {RATES_TO_UAH[target]} UAH",
            f"  Крок 1:     {amount} {source} × {RATES_TO_UAH[source]}"
            f" = {uah.quantize(RATE_PRECISION, rounding=ROUND_HALF_UP)} UAH",
            f"  Крок 2:     {uah.quantize(RATE_PRECISION, rounding=ROUND_HALF_UP)} UAH"
            f" ÷ {RATES_TO_UAH[target]} = {fmt_money(result)} {target}",
            f"  Результат:  {fmt_money(round_money(amount))} {source}"
            f" = {fmt_money(result)} {target}",
        ]
    )


def format_report(amount, source, target):
    bar = "=" * 56
    parts = [bar, "  КОНВЕРТЕР ВАЛЮТ (фіксовані курси)", bar]
    parts += ["Таблиця курсів (1 одиниця з рядка = N одиниць зі стовпця):", ""]
    parts += [format_rates_table(), ""]
    if target == "ALL":
        parts.append(f"Сума {fmt_money(round_money(amount))} {source} у всіх валютах:")
        for dst in CURRENCIES:
            if dst != source:
                parts.append(f"  {dst}: {fmt_money(convert(amount, source, dst)):>14}")
    else:
        parts.append("Розрахунок:")
        parts.append(format_details(amount, source, target))
    parts.append(bar)
    return "\n".join(parts)


def read_input(env, argv):
    if argv:
        if len(argv) != 3:
            raise ValueError("використання: python converter.py СУМА З В")
        raw_amount, raw_from, raw_to = argv
    else:
        raw_amount = env.get("AMOUNT", DEFAULTS["AMOUNT"])
        raw_from = env.get("FROM", DEFAULTS["FROM"])
        raw_to = env.get("TO", DEFAULTS["TO"])
    amount = parse_amount(raw_amount)
    source = normalize_currency(raw_from)
    if str(raw_to).strip().upper() == "ALL":
        return amount, source, "ALL"
    return amount, source, normalize_currency(raw_to)


def main(env=None, argv=None):
    env = os.environ if env is None else env
    argv = sys.argv[1:] if argv is None else argv
    try:
        amount, source, target = read_input(env, argv)
    except ValueError as error:
        print(f"ПОМИЛКА: {error}", file=sys.stderr)
        return 2
    print(format_report(amount, source, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
