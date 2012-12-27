#!/usr/bin/env python
#-*-coding=utf-8-*-

import sys
err = sys.stderr

import nose
import re
from nose.plugins import Plugin


class RegexPicker(Plugin):

    name = "regex_picker"

    def __init__(self):
        super(type(self), self).__init__()
        self.verbose = False

    def options(self, parser, env):
        super(type(self), self).options(parser, env)
        parser.add_option("--re-pattern",
                dest="pattern", action="store",
                default=env.get("NOSE_REGEX_PATTERN", "test.*"),
                help=("Run test methods that have a method name matching\
                this regulat expression"))

    def configure(self, options, conf):
        super(type(self), self).configure(options, conf)
        self.pattern = options.pattern
        if options.verbosity >= 2:
            self.verbosity  = True
            if self.enabled:
                err.write("patern for matching test method is \
                    %s \n" % self.pattern)

    def wantMethod(self, method):
        wanted = \
            re.match(self.patern, method.func_name) is not None
        if self.verbose and wanted:
            err.write("nose will run %s\n" % method.func_name)

        return wanted

if __name__ == "__main__":
    args = ["", "recipel3", \
        "--re-pattern=test.*|length", "--verbosity=2"]

    print "with verbosity..."
    nose.run(argv=args, plugins=[RegexPicker()])
    print "without verbosity..."
    print "====================="
    args = args[:-1]
    nose.run(argv=args, plugins=[RegexPicker()])
