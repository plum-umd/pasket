import os
import shutil
from subprocess import call, Popen, PIPE
import logging

from lib.typecheck import *

from .. import util
from ..sample import Sample

from . import is_event

cur_dir = os.path.dirname(__file__)

root_dir = os.path.join(cur_dir, "..", "..")

lib_dir = os.path.join(root_dir, "lib")
agent_jar = os.path.join(lib_dir, "loggeragent.jar")

smpl_dir = os.path.join(root_dir, "sample")

sim = "Simulator"

@takes(str, str, str)
@returns(nothing)
def gen_aux(cmd, demo, java_dir):
  # extract events from the demo's samples
  smpl_path = os.path.join(smpl_dir, cmd, demo)
  smpl_files = util.get_files_from_path(smpl_path, "txt")

  smpls = []
  for fname in smpl_files:
    smpl = Sample(fname, is_event)
    smpls.append(smpl)

  def evt_to_str(evt): return "\"{}\"".format(evt)

  def smpl_to_arr(smpl):
    return '{' + ", ".join(map(evt_to_str, smpl.evts)) + '}'
  evtss = [ smpl_to_arr(smpl) for smpl in smpls ]

  # generate Simulator.java
  sim_java = sim+".java"
  sim_path = os.path.join(cur_dir, sim_java)
  with open(sim_path, 'r') as f1:
    scenarios = """
    {{
      {}
    }}""".format(",\n".join(evtss))

    raw_body = f1.read()
    sim_body = raw_body.format(**locals())

    sim_path_tgt = os.path.join(java_dir, sim_java)
    with open(sim_path_tgt, 'w') as f2:
      f2.write(sim_body)
      logging.info("generating " + sim_java)

  # generate adapted demo file
  adp_name = "Adapted{demo}".format(**locals())
  # TODO: read the demo;
  # TODO: identify internal elements and make them public (or add getters)

  # generate EventHandler.java
  evt_hdl_java = "EventHandler"+".java"
  evt_hdl_path = os.path.join(cur_dir, evt_hdl_java)
  with open(evt_hdl_path, 'r') as f1:
    # TODO: interpret the given line; generate and feed events to the demo
    handle_code = ''
   
    raw_body = f1.read()
    impl_body = raw_body.format(**locals())

    evt_hdl_path_tgt = os.path.join(java_dir, evt_hdl_java)
    with open(evt_hdl_path_tgt, 'w') as f2:
      f2.write(impl_body)
      logging.info("generating " + evt_hdl_java)


@takes(str, str, list_of(str), str, str)
@returns(int)
def run(cmd, demo, patterns, out_dir, log_fname):
  java_dir = os.path.join(out_dir, "java")
  # generate auxiliary java files
  gen_aux(cmd, demo, java_dir)

  # rename packages
  cwd = os.getcwd()
  os.chdir(out_dir)
  logging.info("renaming package")
  res = call(["./rename-"+cmd+".sh"])
  if res: return res

  # build
  logging.info("building the synthesized model, along with " + demo)
  res = call(["ant"])
  os.chdir(cwd)
  if res: return res

  # run, along with logger agent, and capture logs
  opts = []
  opts.append("-javaagent:{}=time".format(agent_jar))
  opts.extend(["-cp", "bin", sim])

  info = "INFO: "
  p1 = Popen(["java"] + opts, stderr=PIPE)
  p2 = Popen(["grep", info], stdin=p1.stderr, stdout=PIPE)
  f = open(os.path.join(out_dir, log_fname), 'w')
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
        #print "%*s%s" % (indent, "", line[6:])
        f.write("%*s%s\n" % (indent, "", line[6:]))
      elif line[6] == '<':
        #print "%*s%s" % (indent, "", line[6:])
        f.write("%*s%s\n" % (indent, "", line[6:]))
        indent -= 2
    except KeyboardInterrupt: break
  f.close()

  return 0

