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
    def __init__(self, test_plan_id, dryrun=False):
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
        self.dryrun = dryrun
        if self.dryrun:
            def noFun():
                pass
            self.test_run.__del__ = noFun
    def __del__(self):
        # synchronize stuff back
        self.sync()
    def sync(self):
        """synchronize stuff"""
        if self.dryrun:
            logging.info("Won't synchronize updates; dryrun mode")
            return
        for result, testcase in self.result_map.items():
            testcase.update()
            result.update()
        self.test_run.update()

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
            logging.warning("setting status %s skipped; no test case available" %
                    status)
            return
        self.case_run.status = status
        logging.debug("case run %s marked with status: %s" % (self.case_run,
            status))
    def fail(self, log=None):
        """mark current test case run failed"""
        self.status = nitrate.Status('FAILED')
        if log is not None:
           self.add_note(log)
    def success(self, log=None):
        """mark current test case run passed"""
        self.status = nitrate.Status('PASSED')
        if log is not None:
           self.add_note(log)
    def waive(self, log=None):
        """mark current test case run waived"""
        self.status = nitrate.Status('WAIVED')
        if log is not None:
           self.add_note(log)
    def add_note(self, note):
        """add a note to current case run"""
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
        logging.debug("note %s added to case run %s" % (self.case_run, note))

class Translator(object):
    '''The xunit---nitrate transaltor'''
    _case_id_pattern = re.compile('.*tcms(\d+).*')
    def __init__(self, result_path, nitrate):
        self.start_element_map = {
                'testsuite': self.testsuite_start,
                'testcase': self.testcase_start,
                'error': self.error_start,
                'skipped': self.error_start,
                'failure': self.error_start,
              }
        self.end_element_map = {
                'testsuite': self.testsuite_end,
                'testcase': self.testcase_end,
                'error': self.error_end,
                'skipped': self.skipped_end,
                'failure': self.error_end
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
        self.start_element_map[name](args)
    def end(self, name):
        logging.debug("End element <%s/>" % name)
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
        self.nitrate.sync()
    def testcase_start(self, args):
        test_id = self._get_case_id(args['classname'], args['name'])
        if test_id is None:
            logging.info("...skipping non-tcms test: %(classname)s: %(name)s" % args)
            return
        self.nitrate.reset_to_id(test_id)
        self.nitrate.add_note("## %(name)s\n" % args)
    def testcase_end(self):
        """in case status not failed/error/waived it is idle -> mark passed"""
        if self.nitrate.status == nitrate.Status('IDLE'):
            self.nitrate.success(log=self.text)
    def error_start(self, args):
        """just reset text; will read some error details"""
        self.data_reset()
    def error_end(self):
        """current case run set to failed here, because current error cdata
        should be processed now"""
        self.nitrate.fail(log=self.text)
    def skipped_end(self):
        """current case run set to waived here, because current details cdata
        should be processed now"""
        self.nitrate.waive(log=self.text)
    def data_reset(self):
        self.text = ""
    def data(self, text):
        self.text += text
        logging.debug("stored data: %r" % self.text)
    def _get_case_id(self, class_name, test_name):
        try:
            # covers "Context types" as wel
            return int(Translator._case_id_pattern.match(class_name + \
                    test_name).groups()[0])
        except AttributeError:
            # no match results to None -> attribute error
            pass


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

nitrate.setCacheLevel(nitrate.CACHE_CHANGES)

Translator(args.result_file,
        NitrateMaintainer(args.plan_id,
            args.dryrun))
