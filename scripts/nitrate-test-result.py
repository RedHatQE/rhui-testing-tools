#!/usr/bin/env python

import argparse
import logging
import re
import nitrate
from xml.parsers import expat

# deal with arguments
argparser = argparse.ArgumentParser(
    description='Assign test result a Nitrate plan/run id'
    )

argparser.add_argument('--result', help='nosetest xunit result file')
argparser.add_argument('--plan', help='nitrate plan id', type=int)
argparser.add_argument('--debug', help='debug mode', action='store_const',
        const=True)
args = argparser.parse_args()

# deal with logging
if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO
logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
nitrate.log.getLogger().setLevel(loglevel)


class Translator(object):
    '''The xunit---nitrate transaltor'''
    def __init__(self, result_path):
        self.start_element_map = {
                'testsuite': self.testsuite_start,
                'testcase': self.testcase_start,
                'error': self.error_start,
                'skipped': self.skipped_start,
                'failure': self.failure_start,
              }
        self.end_element_map = {
                'testsuite': self.testsuite_end,
                'testcase': self.testcase_end,
                'error': self.error_end,
                'skipped': self.skipped_end,
                'failure': self.failure_end
                }
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.CharacterDataHandler = self.data
        with open(result_path) as result_file:
            logging.debug("Reading results file: %s" % result_path)
            self.parser.ParseFile(result_file)
    def start(self, name, args):
        logging.debug("Start element %s: %s" % (name, args))
        self.start_element_map[name](args)
    def end(self, name):
        logging.debug("End element %s" % name)
        self.end_element_map[name]()
    def testsuite_start(self, args):
        msg = """
Testsuite Stats
  Name:     %(name)s
  Tests:    %(tests)s
  Errors:   %(errors)s
  Failures: %(failures)s
  Skip:     %(skip)s
""" % args
        logging.info(msg)
    def testsuite_end(self):
        pass
    def testcase_start(self, args):
        pass
    def testcase_end(self):
        pass
    def error_start(self, args):
        pass
    def error_end(self):
        pass
    def skipped_start(self, args):
        pass
    def skipped_end(self):
        pass
    def failure_start(self, args):
        pass
    def failure_end(self):
        pass
    def data(self, data):
        pass

### MAIN
translator = Translator(args.result)
