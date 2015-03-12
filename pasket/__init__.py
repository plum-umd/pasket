import os
import traceback
import logging
import logging.config
import subprocess
import sys

from lib.typecheck import *
import lib.const as C

import util

# Terminals used at AST
C.T = util.enum(ANNO="ANNOTATION", \
    PKG="package", CLS="class", ITF="interface", ENUM="enum", \
    EXT="extends", IMP="implements", THROWS="throws", \
    DECL="DECL", FLD="FIELD", MTD="METHOD", \
    TYPE="TYPE", NAME="NAME", PARA="PARAMS", ELT="ELEMS", \
    STM="STAT", EXP="EXPR", ARG="ARGV", CAST="CAST", \
    HOLE=u"??")

# constants regarding Java
C.J = util.enum(MAIN=u"main", CLINIT=u"clinit", \
    T=u"true", F=u"false", N=u"null", \
    NEW="new", THIS=u"this", SUP=u"super", \
    v=u"void", z=u"boolean", b=u"byte", s=u"short", c=u"char", \
    i=u"int", j=u"long", f=u"float", d=u"double", \
    OBJ=u"Object", INT=u"Integer", RUN=u"Runnable", \
    STR=u"String", SB=u"StringBuffer", \
    MAP=u"Map", LST=u"List", STK=u"Stack", QUE=u"Queue", ITER=u"Iterator", \
    TMAP=u"TreeMap", LNK=u"LinkedList", DEQ=u"ArrayDeque")

# Java primitive types
C.primitives = [C.J.z, C.J.b, C.J.s, C.J.c, C.J.i, C.J.j, C.J.f, C.J.d]

# constants regarding Java GUI
C.GUI = util.enum(TOOL=u"Toolkit", QUE=u"EventQueue", \
    EVT=u"EventObject", IVK=u"InvocationEvent")

# constants regarding Android
C.ADR = util.enum(ACTT=u"ActivityThread", QUE=u"MessageQueue", \
    MSG=u"Message", HDL=u"Handler", LOOP=u"Looper", \
    CMP=u"ComponentName", INTT=u"Intent", ACT=u"Activity")

# Java collections
C.collections = [C.J.MAP, C.J.LST, C.J.STK, C.J.QUE, C.J.ITER] \
              + [C.J.TMAP, C.J.LNK, C.J.DEQ]

# type information encodings
C.typ = util.enum(argNum="argNum", argType="argType", retType="retType", \
    belongsTo="belongsTo", subcls="subcls")

C.typ_arrays = [C.typ.argNum, C.typ.argType, C.typ.retType] \
             + [C.typ.belongsTo, C.typ.subcls]

# design patterns
C.P = util.enum(BLD="builder", FAC="factory", SNG="singleton", \
    OBS="observer", PRX="proxy", STA="state", \
    ACCA="accessor_adhoc", ACCU="accessor_uni", ACCM="accessor_map")

# role variables for the accessor pattern
C.ACC = util.enum(AUX=u"AuxAccessor", \
    ACC="accessor", CONS="cons", GET="getter", SET="setter", \
    ADPT="adapter", ADPE="adaptee", FLD="field", \
    GS="gs_field", prvt=u"_prvt_fld")

C.acc_roles = [C.ACC.CONS, C.ACC.GET, C.ACC.SET, C.ACC.GS]

C.adp_roles = [C.ACC.ADPT, C.ACC.ADPE, C.ACC.FLD]

# role variables for the observer pattern
C.OBS = util.enum(AUX=u"AuxObserver", \
    OBSR="observer", SUBJ="subject", EVT="event", \
    A="attach", D="detach", H="handle", U="update", \
    obs=u"_obs", tmp=u"__tmp__")

C.obs_roles = [C.OBS.OBSR, C.OBS.SUBJ, C.OBS.EVT, \
    C.OBS.A, C.OBS.D, C.OBS.H, C.OBS.U]

# role variables for the singleton pattern
C.SNG = util.enum(AUX=u"AuxSingleton", \
    SNG="singleton", INS=u"__instance", GET=u"getter")

C.sng_roles = [C.SNG.SNG, C.SNG.GET]

# artificial classes that may not appear on samples but should be kept
_artifacts = [ \
  u"Platform", \
  C.GUI.TOOL, C.GUI.QUE, C.GUI.EVT, C.GUI.IVK, \
  u"KeyEvent", u"BorderLayout" # TODO: update reducer.remove_cls.mark()
]

@takes(list_of(unicode))
@returns(nothing)
def add_artifacts(cnames):
  global _artifacts
  _artifacts.extend(cnames)


@takes(nothing)
@returns(list_of(unicode))
def get_artifacts():
  global _artifacts
  return _artifacts


from sample import Sample
from meta import class_lookup
from meta.template import Template
from meta.clazz import Clazz
import harness
import reducer
import rewrite
import encoder
import sketch
import decode

pwd = os.path.dirname(__file__)
root_dir = os.path.join(pwd, "..")

smpl_dir = os.path.join(root_dir, "sample")
tmpl_dir = os.path.join(root_dir, "template")

app = "app"

adr = "android"
adr_smpl = os.path.join(smpl_dir, adr)
adr_tmpl = os.path.join(tmpl_dir, adr)
adr_app_tmpl = os.path.join(tmpl_dir, app, adr)

gui = "gui"
gui_smpl = os.path.join(smpl_dir, gui)
gui_tmpl = os.path.join(tmpl_dir, gui)
gui_app_tmpl = os.path.join(tmpl_dir, app, gui)

patt = "pattern"
p_smpl = os.path.join(smpl_dir, patt)
p_tmpl = os.path.join(tmpl_dir, patt)

## Pasket configurations

conf = {}

def configure(opt):
  conf["encoding"] = opt.encoding
  conf["sketch"] = opt.sketch
  conf["randassign"] = opt.randassign
  conf["parallel"] = opt.parallel
  conf["verbose"] = opt.verbose


@takes(str, list_of(str), list_of(str), list_of(str), str, optional(str))
@returns(int)
def main(cmd, smpl_paths, tmpl_paths, patterns, out_dir, log_lv=logging.DEBUG):
  ## logging configuration
  logging.config.fileConfig(os.path.join(pwd, "logging.conf"))
  logging.getLogger().setLevel(log_lv)

  ## check custom codegen was built
  codegen_jar = os.path.join("codegen", "lib", "codegen.jar")
  if not os.path.isfile(codegen_jar):
    raise Exception("can't find " + codegen_jar)

  if cmd == "android":
    tmpl_paths.append(adr_tmpl)
  elif cmd == "gui":
    tmpl_paths.append(gui_tmpl)

  if cmd == "pattern":
    _patterns = patterns[:]
  else: ## android or gui
    _patterns = [C.P.ACCA, C.P.ACCU, C.P.ACCM, \
        C.P.BLD, C.P.FAC, C.P.SNG, C.P.PRX, C.P.OBS, C.P.STA]

  opts = [] ## sketch options
  if conf["verbose"]: opts.extend(["-V", "10"])
  # place to keep sketch's temporary files
  opts.extend(["--fe-tempdir", out_dir])
  opts.append("--fe-keep-tmp")

  tmpls = []
  output_paths = []
  for p in patterns: ## for each pattern or demo
    logging.info("demo: " + p)
    _smpl_paths = smpl_paths[:]
    _tmpl_paths = tmpl_paths[:]

    _smpl_paths.append(os.path.join(smpl_dir, cmd, p))
    if cmd == "pattern":
      client_path = os.path.join(tmpl_dir, cmd, p)
    else: ## android or gui
      client_path = os.path.join(tmpl_dir, app, cmd, p)
    _tmpl_paths.append(client_path)

    ## (smpl|tmpl)_path is either a single file or a folder containing files

    ## read and parse templates
    tmpl_files = []
    for tmpl_path in _tmpl_paths:
      tmpl_files.extend(util.get_files_from_path(tmpl_path, "java"))

    ast = util.toAST(tmpl_files)

    ## convert AST to meta data
    tmpl = Template(ast)

    ## mark client-side classes
    client_files = util.get_files_from_path(client_path, "java")
    for client in client_files:
      base = os.path.basename(client)
      cname = os.path.splitext(base)[0]
      cls = class_lookup(cname)
      cls.client = True

    ## read and parse samples
    smpl_files = []
    for smpl_path in _smpl_paths:
      smpl_files.extend(util.get_files_from_path(smpl_path, "txt"))

    sample.reset()
    smpls = []
    for fname in smpl_files:
      smpl = Sample(fname, tmpl.is_event)
      smpls.append(smpl)

    ## make harness
    harness.mk_harnesses(cmd, tmpl, smpls)

    ## pattern rewriting
    rewrite.visit(cmd, smpls, tmpl, _patterns)
    java_sk_dir = os.path.join(out_dir, '_'.join(["java_sk", p]))
    decode.dump(cmd, java_sk_dir, tmpl)

    ## clean up templates
    #reducer.reduce_anno(smpls, tmpl)
    #reducer.remove_cls(smpls, tmpl)

    tmpl.freeze()
    tmpls.append(tmpl)

    ## encode (rewritten) templates into sketch files
    sk_dir = os.path.join(out_dir, '_'.join(["sk", p]))
    if conf["encoding"]:
      encoder.to_sk(smpls, tmpl, sk_dir)
    else: # not encoding
      logging.info("pass the encoding phase; rather use previous files")

    ## run sketch
    output_path = os.path.join(out_dir, "output", "{}.txt".format(p))
    output_paths.append(output_path)
    if conf["sketch"]:
      if os.path.exists(output_path): os.remove(output_path)

      # custom codegen
      _opts = opts[:]
      _opts.extend(["--fe-custom-codegen", codegen_jar])

      if conf["randassign"] or conf["parallel"]:
        _opts.append("--slv-randassign")
        _opts.extend(["--bnd-dag-size", "16000000"]) # 16M ~> 8G memory

      sketch.set_default_option(_opts)

      if conf["parallel"]:
        ## Python implementation as a CEGIS (sketch-backend) wrapper
        #_, r = sketch.be_p_run(sk_dir, output_path)
        # Java implementation inside sketch-frontend
        _opts.append("--slv-parallel")
        _opts.extend(["--slv-strategy", "WILCOXON"])
        _, r = sketch.run(sk_dir, output_path)
      else:
        _, r = sketch.run(sk_dir, output_path)
      # if sketch fails, halt the process here
      if not r: sys.exit(1)

      ## run sketch again to obtain control-flows
      sketch.set_default_option(opts)
      r = sketch.ctrl_flow_run(sk_dir, output_path, out_dir)
      if not r: sys.exit(1)

    else: # not running sketch
      logging.info("pass sketch; rather read: {}".format(output_path))

    ## end of loop (per pattern/demo)

  ## generate compilable model
  java_dir = os.path.join(out_dir, "java")
  decode.to_java(cmd, java_dir, tmpls, output_paths, _patterns)
  logging.info("synthesis done")

  return 0

