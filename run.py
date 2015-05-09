#!/usr/bin/env python

from optparse import OptionParser

import os
import glob
import subprocess
import sys

# use pyclean to remove *.pyc
# sys.dont_write_bytecode = True

root_dir = os.path.dirname(__file__)

res_dir = os.path.join(root_dir, "result")

def main():
  parser = OptionParser(usage="usage: %prog [options]")
  parser.add_option("-c", "--cmd",
    action="store", dest="cmd",
    type="choice", choices=["android", "gui", "pattern", \
      "grammar", "codegen", "clean"],
    default="android", help="command to run")
  parser.add_option("-p", "--pattern",
    action="append", dest="pattern", default=[],
    help="design pattern or tutorial of interest")
  parser.add_option("-s", "--sample",
    action="append", dest="smpl", default=[],
    help="sample folder")
  parser.add_option("-t", "--template",
    action="append", dest="tmpl", default=[],
    help="template folder")
  parser.add_option("-o", "--output",
    action="store", dest="output", default=res_dir,
    help="output folder")
  parser.add_option("--no-encoding",
    action="store_false", dest="encoding", default=True,
    help="proceed the whole process without the encoding phase")
  parser.add_option("--no-sketch",
    action="store_false", dest="sketch", default=True,
    help="proceed the whole process without running sketch")
  parser.add_option("--randassign",
    action="store_true", dest="randassign", default=False,
    help="run sketch with the concretization feature (not parallel)")
  parser.add_option("--randdegree",
    action="store", dest="randdegree", default=None, type="int",
    help="use sketch's concretization feature, along with the given degree")
  parser.add_option("--parallel",
    action="store_true", dest="parallel", default=False,
    help="run sketch in parallel until it finds a solution")
  parser.add_option("--p_cpus",
    action="store", dest="p_cpus", default=None, type="int",
    help="the number of cores to use for parallel running")
  parser.add_option("--ntimes",
    action="store", dest="ntimes", default=None, type="int",
    help="number of rounds on a single sketch-backend invocation")
  parser.add_option("--simulate",
    action="store", dest="sim", default=None,
    help="what to simulate")
  parser.add_option("--sanity",
    action="store_true", dest="sanity", default=False,
    help="sanity check")
  parser.add_option("-g", "--grammar",
    action="store", dest="grammar", default="Java.g",
    help="grammar description file")
  parser.add_option("-v", "--verbose",
    action="store_true", dest="verbose", default=False,
    help="print intermediate messages verbosely")

  (opt, argv) = parser.parse_args()

  ##
  ## run
  ##
  if opt.cmd == "grammar":
    antlr_jar = os.path.join(root_dir, "lib", "antlr-3.1.3.jar")
    os.environ["CLASSPATH"] = antlr_jar
    antlr_opt = ["org.antlr.Tool", opt.grammar, "-o", "grammar"]
    return subprocess.call(["java"] + antlr_opt)

  elif opt.cmd == "codegen":
    os.chdir(opt.cmd)
    return subprocess.call(["ant"])

  elif opt.cmd == "clean":
    # clean *.pyc
    subprocess.call(["./pyclean"])
    # clean lexer and parser
    for f in glob.glob(os.path.join(root_dir, "grammar", "Java*")):
      os.remove(f)
    # clean custom code generator
    os.chdir("codegen")
    return subprocess.call(["ant", opt.cmd])

  else: # android, gui, or pattern
    if opt.sim or opt.sanity:
      if opt.sanity: opt.sim = opt.pattern[-1]
      import pasket.test as test
      import pasket
      pasket.configure(opt)
      return test.test(opt.cmd, opt.smpl, opt.tmpl, opt.pattern, opt.output, opt.sim)
    else:
      import pasket 
      pasket.configure(opt)
      return pasket.main(opt.cmd, opt.smpl, opt.tmpl, opt.pattern, opt.output)


if __name__ == "__main__":
  sys.exit(main())

