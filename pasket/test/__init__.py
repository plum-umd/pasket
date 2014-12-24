import os
import subprocess
import logging

from lib.typecheck import *

from .. import util
from .. import no_sketch, main

def is_event(mname):
  return util.is_class_name(mname) and "Event" in mname

import simulate
import compare

root_dir = os.path.join(os.path.dirname(__file__), "..", "..")

smpl_dir = os.path.join(root_dir, "sample")

@takes(str, list_of(str), list_of(str), list_of(str), str, str)
@returns(int)
def test(cmd, smpl_paths, tmpl_paths, patterns, out_dir, demo):
  # run the main process to obtain a synthesized model
  no_sketch()
  res = main(cmd, smpl_paths, tmpl_paths, patterns, out_dir)
  if res: return res

  # simulate
  log_fname = os.path.join(out_dir, "simulated.txt")
  res = simulate.run(cmd, demo, patterns, out_dir, log_fname)
  if res: return res

  # compare logs
  smpl_path = os.path.join(smpl_dir, cmd, demo)
  for smpl in util.get_files_from_path(smpl_path, "txt"):
    res = compare.compare(smpl, log_fname)
    if res:
      logging.error("conflict with " + os.path.normpath(smpl))
      return res
    logging.info("compared with " + os.path.normpath(smpl))

  logging.info("test done")
  return 0

