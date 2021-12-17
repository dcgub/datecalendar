// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

/**
 * @title DatesCalendar contract
 * 
 * @dev Extends ERC721 Non-Fungible Token Standard basic implementation.
 */
contract DatesCalendar is ERC721 {


    /**
     * @dev Initialize the contract with the default `name` and `symbol`.
     */
    constructor() public ERC721("DatesCalendar", "DC") {}

}