import os
from kitamanager import berlin
import datetime


def test_berlin_invoice_pay_and_date():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bi = berlin.BerlinInvoice(os.path.join(dir_path, "fixtures/berlin/e_Abrechnung_09-22_0770.xlsx"))
    assert bi.pay == 1500.50
    assert bi.date == datetime.date(2022, 9, 1)


def test_berlin_invoice_children():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bi = berlin.BerlinInvoice(os.path.join(dir_path, "fixtures/berlin/e_Abrechnung_09-22_0770.xlsx"))
    # should be 51 children
    assert len(bi.children) == 51
    # test some of the other data
    assert bi.children["GB-168"]["last_name"] == "Test"
    assert bi.children["GB-168"]["first_name"] == "User46"
    assert bi.children["GB-168"]["pay_tags"] == ["ganztag"]
    assert bi.children["GB-126"]["pay_tags"] == ["ganztag", "integration a"]
    assert bi.children["GB-127"]["pay_tags"] == ["ganztag", "qm/mss"]
    assert bi.children["GB-132"]["pay_tags"] == ["ganztag", "ndh", "qm/mss"]
    assert bi.children["GB-150"]["pay_tags"] == ["teilzeit"]


def test_berlin_invoice_pay_and_date_gte_2025_07():
    """
    test for the new invoice format
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bi = berlin.BerlinInvoice(os.path.join(dir_path, "fixtures/berlin/Abrechnung_11-25_0770.xlsx"))
    assert bi.pay == 1500.50
    assert bi.date == datetime.date(2025, 11, 1)


def test_berlin_invoice_children_gte_2025_07():
    """
    test for the new invoice format
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    bi = berlin.BerlinInvoice(os.path.join(dir_path, "fixtures/berlin/Abrechnung_11-25_0770.xlsx"))
    # should be 51 children
    assert len(bi.children) == 36
    # test some of the other data
    assert bi.children["GB-162"]["last_name"] == "Test"
    assert bi.children["GB-162"]["first_name"] == "User40"
    assert bi.children["GB-162"]["pay_tags"] == ["ganztag"]
    assert bi.children["GB-126"]["pay_tags"] == ["ganztag", "integration a"]
    assert bi.children["GB-127"]["pay_tags"] == ["ganztag", "qm/mss"]
    assert bi.children["GB-132"]["pay_tags"] == ["ganztag", "ndh", "qm/mss"]
    assert bi.children["GB-150"]["pay_tags"] == ["teilzeit"]
