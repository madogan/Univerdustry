# -*- coding: utf-8 -*-
"""Some validation function to validate inputs."""

import re
import ipaddress


def is_integer(s: str) -> bool:
    """Validate a string is in a integer format.

    Args:
        s: Input string.

    Returns:
        :obj:`bool`: True, if input string in integer format.
    """
    try:
        int(s)
        return True
    except Exception:
        return False


def is_comma_separated_integers(s: str) -> [bool, list]:
    """Validate a string is composed of integers separated by comma.

    Examples:
        >>> example_correct_input = "10,20,30,20"

    Args:
        s: Input string.

    Returns:
        :obj:`bool`: True, if validation is ok, else false.
    """

    # If input is not :obj:`str` return false.
    if not isinstance(s, str):
        return False

    # If input is empty, return false.
    if s.strip() == "":
        return False

    # If regex matches, return true.
    elif re.search(r'^([0-9]*,?[0-9]*)*$', s.strip(), re.I | re.U):
        return True

    # If none of them, return true.
    else:
        return False


def is_valid_ip_address(ip_address: str) -> bool:
    """Validate an ip address is correct format.

    Args:
        ip_address: Input ip address.

    Returns:
        :obj:`bool`: True, if validation is ok, else false.
    """

    # If input is not :obj:`str` return false.
    if not isinstance(ip_address, str):
        return False

    # If input is empty, return false.
    if ip_address.strip() == "":
        return False

    # If regex matches, return true.
    elif re.match(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.)'
                  r'{3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|'
                  r'25[0-5])$', ip_address.strip(), re.I | re.UNICODE):
        return True

    # If none of them, return true.
    else:
        return False


def is_fit_str_len_limits(s: str, min_len: int = 1,
                          max_len: int = 255) -> bool:
    """Check a :obj:`str` is a range limit.

    Args:
        s: Input string.
        min_len: Min. length limit.
        max_len: Max. length limit.

    Returns:
        :obj:`bool`: True, if validation is ok, else false.
    """
    # If not :obj:`str` return false.
    if not isinstance(s, str):
        return False

    # If empty return false.
    if s.strip() == "":
        return False

    # If in range return true.
    elif min_len <= len(s) <= max_len:
        return True

    # If none of them, return false.
    else:
        return False


def is_valid_subnet(subnet: str) -> bool:
    """Validate subnet.

    We use a library. If it does not raise an error we return True.

    Examples:
        >>> valid_subnet = "10.255.0.0/24"
        >>> is_valid_subnet(valid_subnet)
        True
        >>> invalid_subnet = "10.256.1.0/25"
        >>> is_valid_subnet(invalid_subnet)
        False

    Args:
        subnet: Subnet string.

    Returns:
        :obj:`bool`: True if given subnet is valid.
    """
    try:
        ipaddress.ip_network(subnet, False)
        return True
    except ValueError:
        return False
