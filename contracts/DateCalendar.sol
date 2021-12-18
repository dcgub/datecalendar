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
     * @dev Returns the number of days since the Unix epoch (1970-01-01).
     */
    function _daysFromUnixEpoch() private view returns (uint256) {
        return block.timestamp / 1 days;
    }

    /**
     * @dev Determines the `dateIndex` given the current block.
     */
     function blockDateIndex() public view returns (uint256) {
        return _unixEpochDateIndex + _daysFromUnixEpoch() - 1;
     }


    /**
     * @dev Determines whether a date index has been released.
     */
     function _isReleased(uint256 dateIndex) private view returns (bool) {
        return dateIndex <= blockDateIndex();
     }


    /**
     * @dev Mint a date calendar token.
     */
    function mintDate(uint256 dateIndex) public {
        require(_isReleased(dateIndex), "DateCalendar: date has not yet been released.");

        _safeMint(msg.sender, dateIndex);

    }

}