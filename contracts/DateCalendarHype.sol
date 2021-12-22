// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title DateCalendar contract
 * 
 * @dev Extends ERC721 Non-Fungible Token Standard basic implementation.
 */
contract DateCalendarHype is ERC721, Ownable {

    using SafeMath for uint256;

    // Unix epoch date (1970-01-01) index
    uint256 private constant _unixEpochDateIndex = 36500;

    // The blockDateIndex upon contract launch
    uint256 public launchBlockDateIndex;

    /**
     * @dev Epoch has a `startDateIndex` and `endDateIndex`,
     * which represent the boundaries of the epoch time interval.
     * A date index belongs in the epoch if it is within the intervel.
     * The interval is closed: startDateIndex <= dateIndex <= endDateIndex.
     */
    struct Epoch {
        uint256 startDateIndex;
        uint256 endDateIndex;
        uint256 releaseDateIndex;
    }

    // Mapping from epoch name to Epoch
    mapping(string => Epoch) public epochs;

    // Maximum amount of epoch releases: Live + 5 others
    uint8 public constant maximumEpochReleases = 6;

    // Array with all epoch names that have been released
    string[] public epochsReleased;

    /**
     * @dev Initialize the contract with the default `name` and `symbol`.
     */
    constructor() public ERC721("DateCalendar", "DC") {
        launchBlockDateIndex = blockDateIndex();

        _defineEpoch('Stub', 0, launchBlockDateIndex);
        _defineEpoch('Live', launchBlockDateIndex, launchBlockDateIndex + 365 * 100);
        releaseEpoch('Live');

    }

    /**
     * @dev Define an epoch for the calendar.
     */
    function _defineEpoch(string memory epochName, uint256 startDateIndex, uint256 endDateIndex) private {
        epochs[epochName] = Epoch(startDateIndex, endDateIndex, 0);
    }  


    /**
     * @dev Checks whether a specific epoch has been defined.
     */
    function _epochDefined(string memory epochName) private view returns (bool) {
        Epoch storage epoch = epochs[epochName];
        if (epoch.startDateIndex == 0 && epoch.endDateIndex == 0) {
            return false;
        }
        return true;
    }  


    /**
     * @dev Release an epoch so that its dates become mintable.
     */
    function releaseEpoch(string memory epochName) public onlyOwner {
        require(epochsReleased.length <= maximumEpochReleases, "DateCalendar: maximum amount of epochs have been released.");
        require(_epochDefined(epochName), "DateCalendar: epoch has not been defined and cannot be released.");

        epochsReleased.push(epochName);

        Epoch storage epoch = epochs[epochName];
        epoch.releaseDateIndex = blockDateIndex() + 7;
    } 

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
        uint256 bdi = blockDateIndex();
        require(dateIndex <= bdi, "DateCalendar: date specified is in the future.");

        string storage epochName;
        Epoch storage epoch;
        for (uint8 i=0; i<epochsReleased.length; i++) {
            epochName = epochsReleased[i];
            epoch = epochs[epochName];
            if (bdi >= epoch.releaseDateIndex) {
                if (dateIndex >= epoch.startDateIndex && dateIndex <= epoch.endDateIndex) {
                    return true;
                }
            }
        }

        return false;
         
     }


    /**
     * @dev Mint a date calendar token.
     */
    function mintDate(uint256 dateIndex) public {
        require(_isReleased(dateIndex), "DateCalendar: date has not yet been released.");

        _safeMint(msg.sender, dateIndex);

    }

}