from brownie import DateCalendar, accounts

def main():
    acct = accounts.load('tests/data/test_account1.json', password='datecalendar')
    acct.deploy(DateCalendar, "DateCalendar", "DC", False)