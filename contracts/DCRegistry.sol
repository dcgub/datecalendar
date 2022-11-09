contract DCRegistry {

	DateCalendar public dc;

	struct Record {
        address resolver;
        uint256 expiry;
	}

    // One record for each date token index
	mapping(uint256 => Record) private _records;

    // Only controllers can set a record
    // Controller can be changed

    // On a controller
    // Only owner of a date can set/change resolver if record is still active.
    // Only owner of date can extend expiry

    // How to add registrar layer that can change pricing etc?

    modifier is_approved_or_owner(uint256 dateTokenIndex) {
        address owner = dc.ownerOf(dateTokenIndex);
        require(owner == msg.sender || dc.getApproved(tokenId) == msg.sender || dc.isApprovedForAll(owner, msg.sender));
        _;
    }

    // Only the owner or an approved operator of the date can set the record...but cannot set ttl
	function setRecord(uint256 dateTokenIndex, address resolver, uint64 ttl) external is_approved_or_owner(dateTokenIndex);

    function resolver(uint256 dateTokenIndex) external view returns (address);

    function ttl(uint256 dateTokenIndex) external view returns (uint64);
}