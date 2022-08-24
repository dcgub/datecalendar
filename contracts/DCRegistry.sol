contract DCRegistry {

	DateCalendar dc;

	struct Record {
        address resolver;
        uint64 ttl;
	}

	mapping(uint256 => Record) private _records;

    modifier is_approved_or_owner(uint256 dateTokenIndex) {
        address owner = dc.ownerOf(dateTokenIndex);
        require(owner == msg.sender || dc.getApproved(tokenId) == msg.sender || dc.isApprovedForAll(owner, msg.sender));
        _;
    }

	function setRecord(uint256 dateTokenIndex) external is_approved_or_owner(dateTokenIndex);

    function resolver(uint256 dateTokenIndex) external view returns (address);

    function ttl(uint256 dateTokenIndex) external view returns (uint64);
}