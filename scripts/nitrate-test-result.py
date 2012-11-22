#!/usr/bin/env python

import argparse
import logging
import re
import nitrate
from xml.parsers import expat

# deal with arguments
argparser = argparse.ArgumentParser(
    description='Assign test result a Nitrate plan/run id',
    epilog="""Remember to fill in your minimal ~/.nitrate file; see pydoc
    nitrate"""
    )

argparser.add_argument('result_file', help='nosetest xunit result file')
argparser.add_argument('plan_id', help='nitrate plan id', type=int)
argparser.add_argument('-d', '--debug', help='debug mode',
        action='store_true')
argparser.add_argument('--dryrun',
        help='no sync will be done to update anything',
        action='store_true')

args = argparser.parse_args()

# deal with logging
if args.debug:
    loglevel = logging.DEBUG
else:
    loglevel = logging.INFO
logging.basicConfig(level=loglevel, format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p')
nitrate.log.getLogger().setLevel(loglevel)


class NitrateMaintainer(object):
    """keeps track of current Nitrate state while parsing"""
    def __init__(self, test_plan_id):
        # load plan and create a run
        self.test_plan = nitrate.TestPlan(id=test_plan_id)
        logging.debug("loaded plan: %s" % self.test_plan)
        self.test_run = nitrate.TestRun(testplan = self.test_plan)
        logging.debug("created plan run: %s" % self.test_run)
        # initialize a result-to-testcase map; this is used for updating
        # a test result record as the parsing goes on
        self.result_map = {}
        for result in self.test_run:
            self.result_map[result.testcase]=result
            # initialize notes as well
        self.reset()
    def sync(self):
        """synchronize stuff with nitrate server"""
        self.test_run.update()
        for result in self.result_map.values():
            result.update()

    def reset(self, test_case = None):
        """reset self state"""
        self.test_case = test_case
        logging.debug("state reset to: %s" % self.test_case)
    def reset_to_id(self, test_id):
        """reset current state to a test_case loaded by the id"""
        logging.debug("resetting to id: %s" % test_id)
        try:
            test_case = nitrate.TestCase(id=test_id)
            if self.test_case == test_case:
                logging.debug("...already at the same id %d" % test_id)
            else:
                # new case id
                if test_case in self.test_plan:
                    logging.debug("...new test_case loaded for id %d" % test_id)
                    self.reset(test_case)
                else:
                    logging.info("...skipped; id %d not in plan" % test_id)
                    self.reset()
        except nitrate.NitrateError as e:
            logging.warning("unmatched test id: %s; error: %s" % (test_id, e))
            self.reset()
    @property
    def in_test(self):
        """check whether parser visited <test>"""
        return self.test_case is not None
    @property
    def case_run(self):
        """return current test case -> case run"""
        if not self.in_test:
            return None
        return self.result_map[self.test_case]
    @property
    def status(self):
        if not self.in_test:
            return None
        return self.case_run.status
    @status.setter
    def status(self, status):
        """update current case run status"""
        if not self.in_test:
            # can't set status if not in test case
            logging.warning("setting status skipped; no test case available (%s)" % status)
            return
        self.case_run.status = status
        logging.debug("case run %s marked with status: %s" % (self.case_run,
            status))
    def add_note(self, note=""):
        """add a note to current case run"""
        if note == "":
            return
        if not self.in_test:
            # can't add note if not in test case
            logging.warning("adding note %s skipped; no test case available" %
                    note)
            return
        try:
            self.case_run.notes += str(note)
        except TypeError:
            # notes is None---first note
            self.case_run.notes = str(note)


class TestCase(object):
    _case_id_pattern = re.compile('.*tcms(\d+).*')
    def __init__(self,
            name=None,
            classname=None,
            status=None,
            log="",
            err=""):
        self.name = name
        self.classname = classname
        self.status = status
        self.log = log
        self.err = err

    def __repr__(self):
        return self.__class__.__name__ + \
                "(name=%(name)r, classname=%(classname)r, status=%(status)r, log=%(log)r, err=%(err)r)" %\
               self.__dict__

    def __str__(self):
        return "%(name)s, %(classname)s, %(status)s" % self.__dict__

    @property
    def id(self):
        try:
            # covers "Context types" as wel
            return int(TestCase._case_id_pattern.match(self.classname + \
                    self.name).groups()[0])
        except AttributeError:
            # no match results to None -> attribute error
            return None



class Translator(object):
    '''The xunit---nitrate transaltor'''
    def __init__(self, result_path, nitrate=None):
        self.start_element_map = {
                'testsuite': self.testsuite_start,
                'testcase': self.testcase_start,
              }
        self.end_element_map = {
                'testsuite': self.testsuite_end,
                'testcase': self.testcase_end,
                'error': self.error_end,
                'skipped': self.skipped_end,
                'failure': self.error_end,
                'system-out': self.system_out_end
                }
        self.data_reset()
        self.nitrate = nitrate
        self.parser = expat.ParserCreate()
        self.parser.StartElementHandler = self.start
        self.parser.EndElementHandler = self.end
        self.parser.CharacterDataHandler = self.data
        with open(result_path) as result_file:
            logging.debug("Reading results file: %s" % result_path)
            self.parser.ParseFile(result_file)

    def start(self, name, args):
        logging.debug("Start element <%s %s>" % (name, args))
        if not self.start_element_map.has_key(name):
            logging.debug("...skipped")
            return
        self.start_element_map[name](args)

    def end(self, name):
        logging.debug("End element <%s/>" % name)
        if not self.end_element_map.has_key(name):
            logging.debug("...skipped")
            return
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
        if not self.nitrate:
            logging.debug("skipping nitrate sync")
            return
        self.nitrate.sync()

    def testcase_start(self, args):
        # have just seen a new testcase
        self.test = TestCase(
                name=args['name'],
                classname=args['classname'],
                status = nitrate.Status('PASSED'))
    def testcase_end(self):
        if self.test.id is None:
            logging.info("skipping non-tcms: %s" % self.test)
            return
        # sync to nitrate
        logging.info("got: %s" % self.test)
        if not self.nitrate:
            logging.debug("skipping nitrate sync")
            return
        self.nitrate.reset_to_id(self.test.id)
        self.nitrate.status = self.test.status
        self.nitrate.add_note(
                "## %s: %s" % (self.test.name, self.test.status) + \
                self.test.err + \
                self.test.log)

    def error_end(self):
        self.test.status = nitrate.Status('FAILED')
        self.test.err = self.text
        self.data_reset()

    def skipped_end(self):
        self.test.status = nitrate.Status('WAIVED')
        self.test.err = self.text
        self.data_reset()

    def system_out_end(self):
        self.test.log = self.text
        self.data_reset()

    def data_reset(self, text=""):
        self.text = text

    def data(self, text):
        self.text += text
        logging.debug("stored data: %r" % self.text)


### MAIN
# Mode of operation:
#  - the result file is read assuming all the tests belong to the nitrate
#    test plan specified
#  - if either test class name or test name in the results file suggests
#    a test change, new Nitrate Test Case instance is loaded from nitrate
#    server specified in one's ~/.nitrate config file
#  - only tests from results file matching the pattern .*tcms(\d+).* are
#    considered
#  - nitrate case id is the number following tcms in the pattern
#  - if a nitrate case id can't be loaded, the test result is skipped
#  - if a nitrate case id isn't present in the nitrate plan specified the test
#    result is skipped
#
# Notes
#  - one's ~/.nitrate configuration is used
#  - minimal nitrate configuration can be figured out issuing pydoc nitrate:
#      [nitrate]
#      url = https://nitrate.server/xmlrpc/
#  - current kerberos ticket is used to authenticate the user if no
#    other login information has been specified in ~/.nitrate

if args.dryrun:
    logging.info("In dry run; no changes will be stored")
    nm = None
else:
    nm = NitrateMaintainer(args.plan_id)
Translator(args.result_file, nm)
