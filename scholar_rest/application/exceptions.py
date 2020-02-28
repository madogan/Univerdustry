# -*- coding: utf-8 -*-
"""Exceptions and catcher script.

This module contains exception classes and generic catcher decorator.
"""


class DefaultException(Exception):
    """Default exception class."""

    def __init__(self, message_index=None):
        self.message_index = message_index or "default_error"

    @property
    def _str(self):
        return self.message_index

    def __str__(self):
        return self._str
