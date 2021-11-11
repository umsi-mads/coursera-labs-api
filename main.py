"""Test script"""

import logging
import pprint
from coursera import Coursera


def main():
    """main"""
    logging.basicConfig(level=logging.DEBUG)
    client = Coursera()
    # course_id = "iL122bLfEemPPg78ueP4bg"
    course_id = "TAoqsmUpEemZsgqSEQNWtg"
    images = client.get_images(course_id)
    pprint.pprint(images)


if __name__ == "__main__":
    main()
