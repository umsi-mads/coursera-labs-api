"""Test script"""

import logging
from coursera_labs import Coursera


def main():
    """main"""
    logging.basicConfig(level=logging.DEBUG)
    client = Coursera()
    client.get_images("ZQnMj8N9EemFBg6_bG2HQg")


if __name__ == "__main__":
    main()
