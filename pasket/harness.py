import cStringIO
from functools import partial
import logging

from lib.typecheck import *
import lib.const as C

from . import add_artifacts
import util
from anno import Anno
from sample import Sample, CallEnt, CallExt, kind
from meta import class_lookup
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


## Android-specific harness body
# launch resource managers and send messages to responsible managers
# e.g., Intent to ActivityManager, MotionEvent to WindowManager, etc.
@takes(Template, Clazz, Sample)
@returns(nothing)
def mk_harness_android(tmpl, cls, smpl):
  harness = mk_harness(cls, smpl)

  buf = cStringIO.StringIO()

  # TODO: launch resource managers

  # TODO: post an Intent for AUT to ActivityManager
  # XXX: rather, start (via ActivityThread.main) and post the Intent to it directly
  main_cls = tmpl.main
  # TODO: passing proper parameters
  buf.write("{}.{}();\n".format(main_cls.clazz.name, main_cls.name))

  # global variables, sort of singletons
  buf.write("""
    {0} l = {0}.getMain{0}();
    {1} q = l.myQueue();
    {2} t = {2}.current{2}();
  """.format(C.ADR.LOOP, C.ADR.QUE, C.ADR.ACTT))

  # generate an Intent to trigger the main Activity
  # TODO: how to figure out the *main* Activity?
  # XXX: assume there is only one Activity
  acts = tmpl.find_cls_kind(C.ADR.ACT)
  if not acts:
    raise Exception("no Activity at all?")
  elif len(acts) > 1:
    raise Exception("no idea what to start among multiple Activity's", acts)
  main_act = acts[0]
  buf.write("""
    {0} c = new {0}(\"{1}\", \"{2}\");
    {3} i = new {3}(c);
  """.format(C.ADR.CMP, "DONT_CARE_PKG_NAME", main_act.name, C.ADR.INTT))

  post = u"q.enqueue{}".format(C.ADR.MSG)

  # TODO: use ActivityManager's Handler
  # XXX: use the main UI thread's Handler
  buf.write("""
    {0} h = t.get{0}();
    {1} m = new {1}(h);
    m.obj = i;
    m.what = -1; // Intent
    {2}(m, 0);
    @React;
  """.format(C.ADR.HDL, C.ADR.MSG, post))

  # additional global variable(s)
  buf.write("""
    {0} a = t.get{0}();
  """.format(C.ADR.ACT))

  cls_ievt = class_lookup(u"InputEvent")

  # post events in the sample to the main Looper's MessageQueue
  evts = smpl.evts
  _hdl = C.ADR.HDL
  _msg = C.ADR.MSG
  logging.debug("# event(s) in {}: {}".format(smpl.name, len(evts)))
  for i, evt in enumerate(evts):
    cls_evt = class_lookup(evt.kind)
    if not cls_evt:
      logging.debug("undeclared event sort: {}".format(evt.kind))
      continue

    e_i = "e{}".format(i)
    init = str(evt)
    buf.write("""
      {evt.kind} {e_i} = new {init};
    """.format(**locals()))

    # generate a message by wrapping the event
    h_i = "h{}".format(i)
    if cls_evt <= cls_ievt: # InputEvent, KeyEvent, MotionEvent
      # TODO: use WindowManager's Handler
      # XXX: use the source View's Handler at the moment
      s_i = "s{}".format(i)
      v_i = "v{}".format(i)
      buf.write("""
        int {s_i} = {e_i}.getSource();
        View {v_i} = a.findViewById({s_i});
        {_hdl} {h_i} = {v_i}.get{_hdl}();
      """.format(**locals()))

    else: # TODO: how to retrieve an appropriate Handler in general?
      buf.write("""
        {_hdl} {h_i} = ...;
      """.format(**locals()))

    m_i = "m{}".format(i)
    e_kind = tmpl.get_event_id(evt.kind)
    buf.write("""
      {_msg} {m_i} = new {_msg}({h_i});
      {m_i}.obj = {e_i};
      {m_i}.what = {e_kind};
    """.format(**locals()))

    # post that message (to the main Looper's MessageQueue)
    buf.write("""
      {post}({m_i}, 0);
      @React;
    """.format(**locals()))

  harness.body = to_statements(harness, unicode(buf.getvalue()))
  cls.add_mtds([harness])


## Swing-specific harness body
# initialize Toolkit and post events via EventQueue.postEvent()
@takes(Template, Clazz, Sample)
@returns(nothing)
def mk_harness_gui(tmpl, cls, smpl):
  harness = mk_harness(cls, smpl)

  buf = cStringIO.StringIO()

  # initialize Toolkit/EventQueue
  buf.write("{0} t = {0}.{1}{0}();\n".format(C.GUI.TOOL, "getDefault"))
  buf.write("{0} q = t.{1}{0}();\n".format(C.GUI.QUE, "getSystem"))

  # run main() in the client
  main_cls = tmpl.main
  # TODO: passing proper parameters
  buf.write("{}.{}();\n".format(main_cls.clazz.name, main_cls.name))
  buf.write("@React;\n") # to handle InvokeEvent

  # post events in the sample to Toolkit's EventQueue
  post = u"q.postEvent"
  evts = smpl.evts
  ev_name = C.GUI.EVT
  logging.debug("# event(s) in {}: {}".format(smpl.name, len(evts)))
  for i, evt in enumerate(evts):
    e_i = "e{}".format(i)
    init = str(evt)
    buf.write("""
      {ev_name} {e_i} = new {init};
    """.format(**locals()))

    e_kind = tmpl.get_event_id(evt.kind)
    buf.write("""
      {e_i}.kind = {e_kind};
      {post}({e_i});
      @React;
    """.format(**locals()))

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

