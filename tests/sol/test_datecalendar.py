import brownie

import pytest

@pytest.fixture(scope="module", autouse=True)
def dc(DateCalendar, accounts):
    owner = accounts[0]
    t = owner.deploy(DateCalendar)
    yield t

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass

def test_mint(dc, accounts, chain):
    acc = accounts[1]
    # First mint
    dc.mintDate(0, {'from': acc})

    # Cannot be minted twice
    with brownie.reverts():
        dc.mintDate(0, {'from': acc})

    # Can mint todoy's date
    today_idx = dc.blockDateIndex()
    dc.mintDate(today_idx, {'from': acc})

    # Cannot mint an index that has
    # not yet been released
    with brownie.reverts():
        dc.mintDate(2**200, {'from': acc})  

    # Cannot mint tomorrow's index
    with brownie.reverts():
        dc.mintDate(today_idx + 1, {'from': acc})   

    # But will work after enough time
    # has passed
    chain.sleep(24 * 60 * 60)
    dc.mintDate(today_idx + 1, {'from': acc})

    # We can also wait for the exact
    # amount of time before minting
    seconds_passed = chain[-1].timestamp % (24 * 60 * 60)
    chain.sleep((24 * 60 * 60) - seconds_passed - 1)
    # Wont work now
    with brownie.reverts():
        dc.mintDate(today_idx + 2, {'from': acc})
    # But will work if we wait 1 second
    chain.sleep(1)
    dc.mintDate(today_idx + 2, {'from': acc})


def test_perpetual_mint(dc, accounts, chain):
    acc = accounts[1]
    today_idx = dc.blockDateIndex()

    for i in range(10):
        today_idx += 1
        # Cannot mint in the future
        with brownie.reverts():
            dc.mintDate(today_idx, {'from': acc})   
        # But can after enough time has passed
        chain.sleep(24 * 60 * 60)
        dc.mintDate(today_idx, {'from': acc}) 

    assert dc.balanceOf(acc) == 10


