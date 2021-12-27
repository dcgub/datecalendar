import datecalendar as dcpy

import brownie

import pytest

import random

@pytest.fixture(scope="module", autouse=True)
def dc(DateCalendar, accounts):
    owner = accounts[0]
    t = owner.deploy(DateCalendar, "DateCalendar", "DC", False)
    yield t

@pytest.fixture(scope="module", autouse=True)
def dc_test(DateCalendar, accounts):
    owner = accounts[0]
    t = owner.deploy(DateCalendar, "DateCalendar", "DC", True)
    yield t

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_base_uri(dc, accounts, chain):
    owner = accounts[0]
    acc = accounts[1]

    dc.mintDate(0, {'from': acc})

    # No base URI has been set so
    # there should be no token URI
    assert dc.tokenURI(0) == ''

    # Random person cannot set URI
    with brownie.reverts():
        dc.setBaseURI('test.com/api/', {'from': acc})

    # Owner can
    dc.setBaseURI('test.com/api/', {'from': owner})

    assert dc.tokenURI(0) == 'test.com/api/0'

    # No URI for token that has not been minted
    with brownie.reverts():
        dc.tokenURI(1)

    dc.mintDate(1, {'from': acc})

    assert dc.tokenURI(1) == 'test.com/api/1'


def test_mint(dc, accounts, chain):
    acc = accounts[1]
    # First mint
    dc.mintDate(0, {'from': acc})

    # Cannot be minted twice
    with brownie.reverts():
        dc.mintDate(0, {'from': acc})

    # Can mint todoy's date
    jd  = dcpy.JulianDate(*dc.currentBlockJD())
    today_dti = jd.to_dti()
    dc.mintDate(today_dti, {'from': acc})

    # Cannot mint an index that has
    # not yet been released
    with brownie.reverts():
        dc.mintDate(2**200, {'from': acc})  

    # Cannot mint tomorrow's index
    with brownie.reverts():
        dc.mintDate(today_dti + 1, {'from': acc})   

    # But will work after enough time
    # has passed
    chain.sleep(24 * 60 * 60)
    dc.mintDate(today_dti + 1, {'from': acc})

    # We can also wait for the exact
    # amount of time before minting
    seconds_passed = chain[-1].timestamp % (24 * 60 * 60)
    chain.sleep((24 * 60 * 60) - seconds_passed - 5)
    # Wont work now
    with brownie.reverts():
        dc.mintDate(today_dti + 2, {'from': acc})
    # But will work if we wait 5 second
    chain.sleep(5)
    dc.mintDate(today_dti + 2, {'from': acc})


def test_perpetual_mint(dc, accounts, chain):
    acc = accounts[1]
    jd  = dcpy.JulianDate(*dc.currentBlockJD())
    today_dti = jd.to_dti()

    for i in range(10):
        today_dti += 1
        # Cannot mint in the future
        with brownie.reverts():
            dc.mintDate(today_dti, {'from': acc})   
        # But can after enough time has passed
        chain.sleep(24 * 60 * 60)
        dc.mintDate(today_dti, {'from': acc}) 

    assert dc.balanceOf(acc) == 10


test_date_data = [
    (-1, 5),
    (0, 5),
    (37, 5),
    (38, 5),
    (1721059, 5),
    (1721118, 5),
    (1721119, 5),
    (1721424, 5),
    (1721425, 5),
    (2299149, 5),
    (2299160, 5),
    (2393470, 5),
    (2400000, 5),
    (2415020, 5),
    (2415385, 5),
    (2440587, 5),
    (2444239, 5),
]

@pytest.mark.parametrize("jd_data", test_date_data)
def test_date_accuracy(dc, accounts, chain, jd_data):
    acc = accounts[1]

    jd = dcpy.JulianDate(*jd_data)
    dti = jd.to_dti()
    py_date = jd.to_gcal_date()

    dc.mintDate(dti, {'from': acc})
    sol_date = dc.proofStringOf(dti)

    assert str(py_date) == sol_date


@pytest.mark.slow
def test_historical_date_accurary(dc_test, accounts, chain):
    dc = dc_test
    acc = accounts[1]

    # For each century from 5000 BCE to 5000 CE,
    # select 10 dates at random and make sure they
    # match the py module.
    start_date = dcpy.GCalDate.from_dmy(1, 1, -4999)
    end_date = dcpy.GCalDate.from_dmy(31, 12, 4999)

    start_dti = start_date.to_jd().to_dti()
    end_dti = end_date.to_jd().to_dti()

    cent_increment = int(365.25 * 100)

    dti = int(start_dti)
    while dti < end_dti:
        random.seed(dti)
        
        dti_seq = random.choices(range(dti, dti + cent_increment), k = 10)
        
        for d in dti_seq:
            py_date = dcpy.DateTokenIndex(d).to_jd().to_gcal_date()

            dc.mintDate(d, {'from': acc})
            sol_date = dc.proofStringOf(d)

            assert str(py_date) == sol_date
            
        
        dti += cent_increment


@pytest.mark.slow
def test_large_date_accurary(dc_test, accounts, chain):
    dc = dc_test
    acc = accounts[1]

    # For each billion years from 20B BCE to 20B CE,
    # select 10 dates at random and make sure they
    # match the py module.
    start_dti, end_dti = dcpy.DateTokenIndex.get_int_bounds()

    b_increment = int(365.25 * 10 ** 9)

    dti = int(start_dti)
    while dti < end_dti:
        random.seed(dti)
        
        dti_seq = random.choices(range(dti, dti + b_increment), k = 10)
        
        for d in dti_seq:
            py_date = dcpy.DateTokenIndex(d).to_jd().to_gcal_date()

            dc.mintDate(d, {'from': acc})
            sol_date = dc.proofStringOf(d)

            assert str(py_date) == sol_date
            
        
        dti += b_increment



