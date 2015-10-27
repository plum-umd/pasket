#!/usr/bin/env python

import json
import os
import sys
import time
from optparse import OptionParser
from subprocess import call, Popen, PIPE

# unbuffered mode (print will be automatically flushed afterwards)
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

root_dir = os.path.join(os.path.dirname(__file__), "..", "..")

logger_dir = os.path.join(root_dir, "logger")
agent_jar = os.path.join(logger_dir, "lib", "loggeragent.jar")

f_log = "log.txt"


def cp_and_main(app=None):
  cps = ["build", "lib/*"]
  if app:
    apps = json.load(open("apps.json"))
    cps.append(apps[app]["src"])
    main = apps[app]["main"]
  else:
    cps.append("src")
    main = "Main"
  return ["-cp", ':'.join(cps), main]


"""
https://blogs.oracle.com/damien/entry/dtrace_java_methods
might need to run this w/ root privilege as follows:
    $ sudo ./run.py
"""
def run_dtrace(args, app=None):
  fst_pid = os.fork()
  if fst_pid == 0:
    opts = []
    opts.append("-XX:+UnlockDiagnosticVMOptions")
    opts.append("-XX:+PauseAtStartup")
    opts.append("-XX:+DTraceMethodProbes")
    opts.extend(cp_and_main(app))
    opts.extend(args)
    call(["java"] + opts)
  else:
    time.sleep(1) # wait for fst_pid running
    vm_paused = None
    for f in os.listdir('.'):
      if os.path.isfile(f) and f.startswith("vm.paused"):
        vm_paused = f
        break
    if vm_paused:
      pid = vm_paused.split('.')[-1]
      snd_pid = os.fork()
      if snd_pid == 0:
        call(["./log_method.d", "-p", pid])
      else:
        time.sleep(1) # wait for snd_pid running
        os.remove(vm_paused)

  return 0


debug = False
agent = True

def run_agent(args, app=None):
  info = "INFO: "
  opts = []
  if agent: opts.append("-javaagent:{}=time".format(agent_jar))
  opts.extend(cp_and_main(app))
  opts.extend(args)

  if debug: return call(["java"] + opts)
  
  p1 = Popen(["java"] + opts, stderr=PIPE)
  p2 = Popen(["grep", info], stdin=p1.stderr, stdout=PIPE)
  p1.stderr.close()
  f = open(f_log, 'w')
  indent = -2
  while True:
    try:
      line = p2.stdout.readline()
      if len(line) == 0: break # EOF
      if not line.startswith(info): continue
      line = line.rstrip("\r\n")
      # "INFO: (>|<) ..."
      if line[6] == '>':
        indent += 2
        print "%*s%s" % (indent, "", line[6:])
        f.write("%*s%s\n" % (indent, "", line[6:]))
      elif line[6] == '<':
        print "%*s%s" % (indent, "", line[6:])
        f.write("%*s%s\n" % (indent, "", line[6:]))
        indent -= 2
    except KeyboardInterrupt: break
  f.close()

  return 0


def main():
  parser = OptionParser(usage="usage: %prog [options]")
  parser.add_option("-c", "--cmd",
    action="store", dest="cmd",
    type="choice", choices=["dtrace", "agent"], default="agent",
    help="command to run")
  parser.add_option("--app",
    action="append", dest="apps", default=[],
    help="application(s) under test")
  parser.add_option("-d", "--debug",
    action="store_true", dest="debug", default=False,
    help="run examples without post processing")
  parser.add_option("--no-agent",
    action="store_false", dest="agent", default=True,
    help="run without logging agent")

  (opt, args) = parser.parse_args()

  global debug, agent
  debug = opt.debug
  agent = opt.agent

  f = globals()["run_" + opt.cmd]
  if opt.apps:
    for app in opt.apps:
      r = f(args, app)
      if r: return r
  else:
    return f(args)


if __name__ == "__main__":
  sys.exit(main())

