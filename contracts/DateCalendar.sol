// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

/**
 * @title DateCalendar contract
 * 
 * @dev Extends ERC721 Non-Fungible Token Standard basic implementation.
 */
contract DateCalendar is ERC721 {

	// Unix epoch date (1970-01-01) index
	uint256 private constant _unixEpochDateIndex = 36500;

    /**
     * @dev Initialize the contract with the default `name` and `symbol`.
     */
    constructor() public ERC721("DateCalendar", "DC") {}

    /**
     * @dev Mint a date calendar token.
     */
    function mintDate(uint256 dateIndex) public {

    	_safeMint(msg.sender, dateIndex);

    }

}