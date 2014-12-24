#! /usr/bin/env python

from optparse import OptionParser

import sys
import re

def comment(line, uncomment=False):
  #   //  (>|<)x.y...
  # =>  (>|<)x.y...
  if uncomment: return line[2:]
  #     (>|<)x.y...
  # =>//  (>|<)x.y...
  else: return "//"+line

log_regex = r".*(>|<) (.*)\((.*)\)"

def main():
  parser = OptionParser(usage="usage: %prog [options] smpl")
  parser.add_option("-c", "--component",
    action="append", dest="comps", default=[],
    help="specify components of interest")
  parser.add_option("-o", "--output",
    action="store", dest="output", default="output.txt",
    help="output file")
  parser.add_option("--uncomment",
    action="store_true", dest="uncomment", default=False,
    help="uncomment components of interest")

  (opt, argv) = parser.parse_args()

  if len(argv) < 1:
    parser.error("no sample")
  if not opt.comps:
    parser.error("no components")

  def find_comp(cls):
    comps = filter(lambda comp: comp == cls, opt.comps)
    if any(comps): return cls
    else: return None

  with open(argv[0], 'r') as f1:
    with open(opt.output, 'w') as f2:
      in_mtd = None
      for line in f1.readlines():
        if in_mtd: f2.write(comment(line, opt.uncomment))
        m = re.match(log_regex, line)
        if m:
          indicator = m.group(1)
          mid = m.group(2).split('.')
          cls, mtd = mid[-2], mid[-1]
        else: raise Exception("wrong call sequences", line)
        if in_mtd == '.'.join([cls, mtd]) and indicator == '<':
          in_mtd = None
        elif not in_mtd:
          if find_comp(cls):
            in_mtd = '.'.join([cls, mtd])
            f2.write(comment(line, opt.uncomment))
          else:
            f2.write(line)

if __name__ == "__main__":
  sys.exit(main())

