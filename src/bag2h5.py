#!/usr/local/bin/python2.7
# encoding: utf-8
'''
bag2h5 -- Transform ROS bags into HDF5

@author:     Léonard Gérard

@copyright:  2015, All rights reserved.

@contact:    leonard.gerard@sri.com
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import logging
import sys

from pathlib import Path
import colorlog

from ros2scipy.bag2h5 import folder2h5, bag2h5, checkfolder2h5, checkh5bag

__version__ = 0.1
__date__ = '2015-10-15'
__updated__ = '2015-10-15'

DEBUG = 1

def main():

    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by Léonard Gérard on %s.
  Copyright 2015 organization_name. All rights reserved.

''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-r", "--recursive", action="store_true", help="recurse into subfolders [default: %(default)s]")
        parser.add_argument("--db_root", default="/", help="The group to be considered as root for new datasets [default: %(default)s]")
        parser.add_argument("--topic_filter", nargs='*', default=["/rosout", "/rosout_agg"], help="The topics to discard in the process [default: %(default)s]")
        parser.add_argument("-v", "--verbose", action="count", help="set verbosity level [default: %(default)s]")
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-o', '--output', default="bags.h5", help="HDF5 file to create/append the bag datasets [default: %(default)s]")
        parser.add_argument('-cpm', '--custom_parser_modules', action='append', default=[], help="Python modules from which to load custom_parsers. They need to be on the pythonpath.")
        parser.add_argument(dest="bags", nargs='+', help="bag files or folders to convert")

        # Process arguments
        args = parser.parse_args()
        args_dict = vars(args) # allow the use of args as a dictionnary (it is a Namespace)

        # logging facility
        if args.verbose <= 0:
            logging.root.setLevel(logging.ERROR)
        elif args.verbose == 1:
            logging.root.setLevel(logging.INFO)
        else:
            logging.root.setLevel(logging.DEBUG)
        colorlog.basicConfig(format="%(log_color)s%(levelname)s%(reset)s:%(message)s")

        db = args.output

        for f in args.bags:
            f = Path(f)
            if f.is_dir():
                folder2h5(f, db, **args_dict)
                checkfolder2h5(f, db, **args_dict)
            elif f.is_file():
                bag2h5(f, db, **args_dict)
                checkh5bag(f, db, **args_dict)
            else:
                logging.warning("Path {} isn't a correct file or folder, skipping it.".format(f))
        return 0

    except KeyboardInterrupt:
        logging.error("User interrupted while ...") # TODO: actually gather what we were doing
        return 1

    except Exception as e:
        if DEBUG:
            raise(e)
        logging.exception("Internal error")
        return 2

if __name__ == "__main__":
    sys.exit(main())

