#! /usr/bin/env python

import glob
import os
from optparse import OptionParser
import pprint
import re
import sys

f_trial_re = re.compile(r"parallel trial.* \((\d+)\) failed")
s_trial_re = re.compile(r"parallel trial.* \((\d+)\) solved")
ttime_re = re.compile(r"Total time = ([+|-]?(0|[1-9]\d*)(\.\d*)?([eE][+|-]?\d+)?)")

be_separator_re = re.compile(r"=== parallel trial.* \((\d+)\) (\S+) ===")

def analyze(output):
  bname = os.path.basename(output)
  b = os.path.splitext(bname)[0]

  record = {}
  record["benchmark"] = b

  is_parallel = False

  with open(output, 'r') as f:
    f_trial = -1
    s_trial = -1
    ttime = -1
    f_times = []
    s_times = []
    lines = []
    for line in f:
      ## information from front-end
      m = re.search(f_trial_re, line)
      if m:
        _f_trial = int(m.group(1))
        f_trial = max(f_trial, _f_trial)

      else:
        m = re.search(s_trial_re, line)
        if m:
          _s_trial = int(m.group(1))
          if s_trial < 0: s_trial = _s_trial
          else: s_trial = min(s_trial, _s_trial)

      m = re.search(ttime_re, line)
      if m:
        # to filter out the final Sketch run for CFG retrieval
        ttime = max(ttime, int(float(m.group(1))))

      ## information from back-end
      m = re.search(be_separator_re, line)
      if m:
        is_parallel = True
        if m.group(2) in ["failed", "solved"]:
          record = be_analyze_lines(lines, b)
          if record["succeed"] == "Succeed":
            s_times.append(record["ttime"])
          else: # "Failed"
            f_times.append(record["ttime"])

          lines = []

      else:
        lines.append(line)

    # for plain Sketch, the whole message is from back-end
    if not is_parallel:
      record = be_analyze_lines(lines, b)
      if record["succeed"] == "Succeed":
        s_times.append(ttime)
      else: # "Failed"
        f_times.append(ttime)

    trial = len(f_times) + len(s_times)
    record["trial"] = max(trial, s_trial)
    s_succeed = "Succeed" if any(s_times) else "Failed"
    record["succeed"] = s_succeed
    f_time_sum = sum(f_times)
    s_time_sum = sum(s_times)
    record["ttime"] = ttime
    record["stime"] = float(s_time_sum) / len(s_times) if s_times else 0
    record["ftime"] = float(f_time_sum) / len(f_times) if f_times else 0
    record["ctime"] = f_time_sum + s_time_sum

  return record


exit_re = re.compile(r"Solver exit value: ([-]?\d+)")
be_tout_re = re.compile(r"timed out: (\d+)")
be_etime_re = re.compile(r"elapsed time \(s\) .* ([+|-]?(0|[1-9]\d*)(\.\d*)?([eE][+|-]?\d+)?)")
be_stime_re = re.compile(r"Total elapsed time \(ms\):\s*([+|-]?(0|[1-9]\d*)(\.\d*)?([eE][+|-]?\d+)?)")
be_ttime_re = re.compile(r"TOTAL TIME ([+|-]?(0|[1-9]\d*)(\.\d*)?([eE][+|-]?\d+)?)")


def be_analyze_lines(lines, b):
  record = {}
  record["benchmark"] = b

  exit_code = -1
  etime = 0
  ttime = 0
  timeout = None
  succeed = False
  propagation = -1
  for line in reversed(lines):
    m = re.search(exit_re, line)
    if m:
      exit_code = int(m.group(1))
      succeed |= exit_code == 0
    if "ALL CORRECT" in line:
      succeed |= True
    if "[SKETCH] DONE" in line:
      succeed |= True

    m = re.search(be_ttime_re, line)
    if m:
      ttime = ttime + int(float(m.group(1)))
    m = re.search(be_stime_re, line)
    if m:
      etime = float(m.group(1))
    m = re.search(be_tout_re, line)
    if m:
      timeout = int(m.group(1))

  for line in lines:
    m = re.search(be_etime_re, line)
    if m:
      etime = int(float(m.group(1)) * 1000)
      break

  s_succeed = "Succeed" if succeed else "Failed"
  record["succeed"] = s_succeed
  if timeout: _time = timeout
  elif etime: _time = etime
  else: _time = ttime
  record["ttime"] = _time

  return record


def main():
  parser = OptionParser(usage="usage: %prog [options]")
  parser.add_option("-b", "--benchmark",
    action="append", dest="benchmarks", default=[],
    help="benchmark(s) under analysis")
  parser.add_option("-d", "--dir",
    action="store", dest="out_dir", default="output",
    help="output folder")

  (opt, args) = parser.parse_args()

  outputs = glob.glob(os.path.join(opt.out_dir, "*.txt"))
  # filter out erroneous cases (due to broken pipes, etc.)
  outputs = filter(lambda f: os.path.getsize(f) > 0, outputs)

  for output in outputs:
    bname = os.path.basename(output)
    if any(opt.benchmarks):
      found = False
      for b in opt.benchmarks:
        found |= bname.startswith(b)
        if found: break
      if not found: continue

    record = analyze(output)
    pprint.pprint(record)


if __name__ == "__main__":
  sys.exit(main())

