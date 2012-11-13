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
    def __del__(self):
        # synchronize stuff back
        self.sync()
    def sync(self):
        """synchronize stuff"""
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
        return self.result_map[self.test_case]
    @property
    def status(self):
        return self.case_run.status
    @status.setter
    def status(self, status):
        """update current case run status"""
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
        try:
            self.case_run.notes.append(str(note))
        except AttributeError:
            # notes is None
            self.case_run.notes = [str(note)]
        logging.debug("note %s added to case run %s" % (self.case_run, note))

class Translator(object):
    '''The xunit---nitrate transaltor'''
    _case_id_pattern = re.compile('.*tcms(\d+).*')
    def __init__(self, result_path, test_plan_id):
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
        self.nitrate = NitrateMaintainer(test_plan_id)
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
translator = Translator(args.result, args.plan)
