from dataclasses import dataclass
from dateparser import parse
from pypdf import PdfReader
from decimal import Decimal


@dataclass
class PayrollPerson:
    """
    A Person from a Payroll
    """

    first_name: str
    last_name: str
    hours: int
    pay_group: int
    pay_level: int


class SagePayrolls:
    """
    Parse a Sage Payroll (Lohn/Gehaltsabrechnung) PDF file with multiple pages. Each page contains a single person
    The file is expected to be in German and currently very eenemeene specific
    """

    def __init__(self, lohnscheine_path: str):
        self._lohnscheine_path = lohnscheine_path
        self._reader = PdfReader(self._lohnscheine_path)
        self._date = None

    def _get_date(self, text_split):
        for count, line in enumerate(text_split):
            if line.endswith("Abrechnungsmonat:"):
                date_str = text_split[count + 1].split("#")[0]
                date = parse(date_str).replace(day=1)
                return date
        return None

    def _get_person(self, text_split):
        for count, line in enumerate(text_split):
            # FIXME: very eenemeene specific
            if line.startswith("TV-EM"):
                parts = line.split(" ")
                assert parts[0] == "TV-EM"
                pay_group = int(parts[1].replace("S", ""))
                assert pay_group >= 3 and pay_group <= 10
                pay_level = int(parts[2].replace("(", "").replace(")", ""))
                assert pay_level >= 1 and pay_level <= 6
                hours = Decimal(parts[4])
                assert hours >= 0 and hours <= 40
                # < 2025 have name in the same line, later name is in next line
                # eg. later it is: ['TV-EM S6 (3)  30 h', 'Firstname Lastname']
                first_name = parts[5][1:]
                last_name = " ".join(parts[6:])
                if not first_name:
                    first_name, last_name = text_split[count + 1].split(" ")
                return PayrollPerson(
                    first_name=first_name, last_name=last_name, hours=hours, pay_group=pay_group, pay_level=pay_level
                )
        return None

    @property
    def date(self):
        # cache the date
        if not self._date:
            # just use the first page and assume that all pages are for the same date
            page = self._reader.pages[0]
            text = page.extract_text()
            text_split = text.splitlines()
            self._date = self._get_date(text_split)
        return self._date

    @property
    def persons(self):
        """
        Parse the different PDF pages and return a list of persons
        """
        persons = []
        for page_number, page in enumerate(self._reader.pages):
            text = page.extract_text()
            text_split = text.splitlines()
            person = self._get_person(text_split)
            if person:
                persons.append(person)
        return persons
