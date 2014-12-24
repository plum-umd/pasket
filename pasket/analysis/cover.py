#!/usr/bin/env python

import logging
import os
import sys

from lib.typecheck import *

from .. import util
from ..meta import class_lookup, methods
from ..meta.template import Template
from ..meta.clazz import find_mtd
from ..meta.method import find_formals

from api import APICollector

@takes(list_of(str), list_of(str))
@returns(bool)
def covered(tmpl_files, demo_files):
  ast = util.toAST(tmpl_files + demo_files)

  tmpl = Template(ast)

  ## mark client-side classes
  for client in demo_files:
    base = os.path.basename(client)
    cname = os.path.splitext(base)[0]
    cls = class_lookup(cname)
    cls.client = True

  collector = APICollector()
  tmpl.accept(collector)

  def find_api(cname, mname, arg_typs):
    mtd = find_mtd(cname, mname, arg_typs)
    if mtd: return True, [mtd]

    candidates = []
    for mtd in methods():
      if mtd.name == mname:
        if mtd.clazz.name == cname:
          candidates.append(mtd)
        else:
          sup = mtd.clazz.in_hierarchy(lambda cls: cls.name == cname)
          if sup: candidates.append(mtd)

    return False, candidates

  missed = False
  for cname, mname, arg_typs in collector.APIs:
    found, mtds = find_api(cname, mname, arg_typs)
    if found:
      logging.debug("modeled: {}".format(mtds[0].signature))
    else:
      missed = True
      argv = ", ".join(arg_typs)
      logging.info("missed: {}.{}({})".format(cname, mname, argv))
      for candidate in mtds:
        logging.info("  candidate: {}".format(candidate.signature))

  return not missed


"""
To import lib.*, run as follows:
  pasket $ python -m spec.analysis.cover [-t tmpl_path] (demo_file | demo_path)+
"""
if __name__ == "__main__":
  from optparse import OptionParser
  usage = "usage: %prog [-t tmpl_path] demo_path"
  parser = OptionParser(usage=usage)
  parser.add_option("-c", "--cmd", # same as run.py at the top level
    action="store", dest="cmd",
    type="choice", choices=["android", "gui", "pattern", \
      "grammar", "codegen", "clean"],
    default="gui", help="command to run")
  parser.add_option("-t", "--template", # same as run.py at the top level
    action="append", dest="tmpl", default=[],
    help="template folder")

  (opt, argv) = parser.parse_args()

  if len(argv) < 1:
    parser.error("incorrect number of arguments")

  pwd = os.path.dirname(__file__)
  spec_dir = os.path.join(pwd, "..")
  root_dir = os.path.join(spec_dir, "..")
  sys.path.append(root_dir)

  ## logging configuration
  logging.config.fileConfig(os.path.join(spec_dir, "logging.conf"))
  logging.getLogger().setLevel(logging.DEBUG)

  tmpls = opt.tmpl[:]
  if not tmpls:
    tmpl_dir = os.path.join(root_dir, "template", opt.cmd)
    tmpls.append(tmpl_dir)

  tmpl_files = []
  for tmpl_path in tmpls:
    tmpl_files.extend(util.get_files_from_path(tmpl_path, "java"))

  demo_files = []
  for arg in argv:
    demo_files.extend(util.get_files_from_path(arg, "java"))

  covered(tmpl_files, demo_files)

