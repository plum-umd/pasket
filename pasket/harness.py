import cStringIO
from functools import partial
import logging

from lib.typecheck import *
import lib.const as C

from . import add_artifacts
import util
from anno import Anno
from sample import Sample, CallEnt, CallExt, kind
from meta.template import Template
from meta.clazz import Clazz
from meta.method import Method
from meta.statement import Statement, to_statements
from meta.expression import to_expression

## common part: generate a harness method
@takes(Clazz, Sample)
@returns(Method)
def mk_harness(cls, smpl):
  _anno = Anno(name=C.A.HARNESS, f=smpl.name)
  mtd = Method(clazz=cls, annos=[_anno], mods=C.PBST, name=unicode(smpl.name))
  logging.debug("adding {} {}.{}".format(str(_anno), cls.name, mtd.name))
  return mtd


## common part: code snippets to set environment changes
@takes(Template, Sample, unicode, optional(bool), optional(unicode))
@returns(unicode)
def gen_events(tmpl, smpl, post, react_immediately=False, ev_name=u"Event"):
  evts = smpl.evts
  logging.debug("# event(s) in {}: {}".format(smpl.name, len(evts)))
  buf = cStringIO.StringIO()
  for i, evt in enumerate(evts):
    e_i = "e{}".format(i)
    init = str(evt)

    if ev_name == "Event":
      e_lower = evt.kind.lower()
      buf.write("""
        {ev_name} {e_i} = new {ev_name}();
        {e_i}.{e_lower} = new {init};
      """.format(**locals()))
    else: # Java GUI
      buf.write("""
        {ev_name} {e_i} = new {init};
      """.format(**locals()))

    e_kind = tmpl.events[evt.kind]
    buf.write("""
      {e_i}.kind = {e_kind};
      {post}({e_i});
    """.format(**locals()))

    if react_immediately:
      buf.write("@React;\n")

  return unicode(buf.getvalue())


## Android-specific harness body
@takes(Template, Clazz, Sample)
@returns(nothing)
def mk_harness_android(tmpl, cls, smpl):
  harness = mk_harness(cls, smpl)
  # TODO
  cls.add_mtds([harness])


## Swing-specific harness body
# initialize Toolkit and post events via EventQueue.postEvent()
@takes(Template, Clazz, Sample)
@returns(nothing)
def mk_harness_gui(tmpl, cls, smpl):
  harness = mk_harness(cls, smpl)

  buf = cStringIO.StringIO()

  # Toolkit initialization
  buf.write("{0} t = {0}.{1}{0}();\n".format(C.GUI.TOOL, "getDefault"))
  buf.write("{} q = t.getSystemEventQueue();\n".format(C.GUI.QUE))

  # run the application
  main_cls = tmpl.main
  # TODO: passing proper parameters
  buf.write("{}.{}();\n".format(main_cls.clazz.name, main_cls.name))
  buf.write("@React;\n") # to handle InvokeEvent

  # post events in the sample to the event queue
  post = u"q.postEvent"
  buf.write(gen_events(tmpl, smpl, post, True, C.GUI.EVT))
  harness.body = to_statements(harness, unicode(buf.getvalue()))
  cls.add_mtds([harness])


## general harness body
# create objects and make relations among them according to the given sample
@takes(Template, Clazz, Sample)
@returns(nothing)
def mk_harness_pattern(tmpl, cls, smpl):
  harness = mk_harness(cls, smpl)

  buf = cStringIO.StringIO()

  call_stack = []

  objs = {} # { @Object(typ, idx): obj_typ_idx, ... }
  def lkup_obj(v):
    if type(kind(v)) is unicode: return objs[v]
    else: return v

  def to_obj(v):
    _anno = to_expression(v).anno
    rep = u"obj_{}_{}".format(_anno.typ, _anno.idx)
    objs[v] = rep
    return rep

  for i, log in enumerate(smpl.logs):
    if isinstance(log, CallEnt):
      call_stack.append(log)
      if len(call_stack) > 1: continue

      if log.is_init:
        rcv = to_obj(smpl.logs[i+1].vals[0])
        args = ", ".join(map(lkup_obj, log.vals))
        buf.write("{0} {1} = new {0}({2});\n".format(log.cls, rcv, args))

      else: # normal call
        try:
          args = map(lkup_obj, log.vals)
          if log.vals and type(kind(log.vals[0])) is unicode:
            args_mod_rcv = ", ".join(args[1:])
            buf.write("{}.{}({});\n".format(args[0], log.mtd, args_mod_rcv))
          else: buf.write("{}({});\n".format(log.mtd, ", ".join(args)))
        except KeyError: continue # means, unknown obj (Evt) occurs

    elif isinstance(log, CallExt):
      call_stack.pop()
      if len(call_stack) > 0: continue

    else: # Evt
      buf.write("@React;\n")

  harness.body = to_statements(harness, unicode(buf.getvalue()))
  cls.add_mtds([harness])


@takes(str, Template, list_of(Sample))
@returns(nothing)
def mk_harnesses(cmd, tmpl, smpls):
  f = globals()["mk_harness_" + cmd]
  main_cls = Clazz(name=u"Main")
  tmpl.add_classes([main_cls])
  add_artifacts([u"Main"])
  map(partial(f, tmpl, main_cls), smpls)

