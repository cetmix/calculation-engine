# Copyright (C) 2024 Cetmix OÜ
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).


class AttrDict(dict):
    """
    A dictionary subclass that supports accessing its keys as attributes.

    Enables attribute-style access to dictionary items, allowing for easy
    reading, assigning, or deleting of key-value pairs using dot notation.
    """

    def __getattr__(self, item):
        """
        Enables attribute-style read access to dictionary items.

        Args:
            item (str): The attribute (key) to access.

        Returns:
            The value associated with 'item'.

        Raises:
            AttributeError: If 'item' is not a key in the dictionary.
        """
        try:
            return self[item]
        except KeyError as err:
            raise AttributeError(
                f"'AttrDict' object has no attribute '{item}'"
            ) from err

    def __setattr__(self, key, value):
        """
        Allows setting dictionary items as attributes.

        Args:
            key (str): The attribute (key) to set.
            value: The value to assign to 'key'.
        """
        self[key] = value

    def __delattr__(self, item):
        """
        Enables attribute-style deletion of dictionary items.

        Args:
            item (str): The attribute (key) to delete.

        Raises:
            AttributeError: If 'item' is not a key in the dictionary.
        """
        try:
            del self[item]
        except KeyError as err:
            raise AttributeError(
                f"'AttrDict' object has no attribute '{item}'"
            ) from err
