"""Test script"""

import logging
from coursera import Coursera
import sys


def main():
    """main"""
    logging.basicConfig(level=logging.DEBUG)
    client = Coursera()
    print(client.whoami())

    # client.get_course("siads505")
    course_id = "iL122bLfEemPPg78ueP4bg"
    # course_id = "TAoqsmUpEemZsgqSEQNWtg"
    images = client.get_images(course_id)

    for image in images:
        print("Image: {}".format(image.name))

        try:
            labs = client.get_labs(course_id, image.id)
        except RuntimeError:
            print("  Unable to properly fetch labs.")
            continue

        for lab in labs:
            print("  Lab: {}".format(lab.name))

            items = client.get_lab_items(course_id, image.id, lab.id)

            for item in items:
                print("    Item: {}".format(item))


if __name__ == "__main__":
    main()
