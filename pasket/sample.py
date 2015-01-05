#!/usr/bin/env python

import os
import re
import operator as op
from itertools import chain
import ast
import string
import sys
import logging

from lib.typecheck import *
import lib.const as C

import util

class CallBase(object):

  # (>|<) pkg...cls.mtd(val1, val2, ...)
  def __init__(self, line, depth=0):
    self._depth = depth
    m = re.match(r"(>|<) (.*)\((.*)\)", line)
    if m: # m.group(1) = '>' or '<'
      self._pkg, self._cls, self._mtd = util.explode_mname(m.group(2))
      vals = map(op.methodcaller("strip"), m.group(3).split(','))
      self._vals = util.ffilter(vals) # to remove empty strings
    else:
      raise Exception("wrong call sequences", line)

  def __str__(self):
    mid = []
    if self._pkg: mid.append(self._pkg)
    mid.extend([self._cls, self._mtd])
    return '.'.join(mid) + '(' + ", ".join(map(str, self._vals)) + ')'

  @property
  def indent(self):
    return ' ' * (self._depth * 2)

  @property
  def pkg(self):
    return self._pkg    

  @property
  def cls(self):
    return self._cls

  @property
  def mtd(self):
    return self._mtd

  @property
  def vals(self):
    return self._vals

  @vals.setter
  def vals(self, v):
    self._vals = v

  @property
  def is_init(self):
    return self._cls == self._mtd


# >
class CallEnt(CallBase):
  def __str__(self):
    return self.indent + "> " + super(CallEnt, self).__str__()


# <
class CallExt(CallBase):
  def __str__(self):
    return self.indent + "< " + super(CallExt, self).__str__()


class Evt(object):

  # sort(val1, val2, ...)
  def __init__(self, **kwargs):
    if "line" in kwargs.keys():
      line = kwargs["line"]
      m = re.match(r"(.*)\((.*)\)", line)
      if m:
        self._kind = m.group(1)
        vals = map(op.methodcaller("strip"), m.group(2).split(','))
        self._vals = filter(None, vals) # to remove empty strings
      else:
        raise Exception("wrong environmental changes", line)
    else:
      for key in kwargs:
        setattr(self, key, kwargs[key])

  def __str__(self):
    return self._kind + '(' + ", ".join(map(str, self._vals)) + ')'

  @property
  def kind(self):
    return self._kind

  @property
  def vals(self):
    return self._vals

  @vals.setter
  def vals(self, v):
    self._vals = v

  @property
  def sources(self):
    # assume runtime instances are of the form: @Object(typ=..., idx=...)
    def obj_finder(val):
      m = re.match(r"@Object\(typ=(.+), idx=\d+\)", val)
      if m: return m.group(1)
      else: return None
    return util.rm_dup(util.rm_none(map(obj_finder, self._vals)))


class Sample(object):

  def __init__(self, fname, is_event):
    self._name, _ = os.path.splitext(os.path.basename(fname))
    self._logs = []  # list of CallEnt, CallExt, or Evt
    self._decls = {} # { cls1: (mtd1, mtd2, ...), ... }
    self._objs = {} # { cname0: ( hsh0, ... ), cname1: ( hsh1, ... ), ... }
    self._num_objs = 0

    with open(fname) as f:
      logging.debug("reading sample: " + os.path.normpath(f.name))
      depth = 0
      for line in f.readlines():
        line = unicode(line.strip())
        try:
          if line[0] == '>':
            log = CallEnt(line, depth)
            depth = depth + 1
          elif line[0] == '<':
            depth = depth - 1
            log = CallExt(line, depth)
          elif line[0] in string.ascii_letters:
            log = Evt(line=line)
          else: continue # comments or something
        except IndexError: continue # empty line

        if line[0] == '>':
          if log.is_init and is_event(log.mtd):
            log = Evt(_kind=log.mtd, _vals=log.vals)
        elif line[0] == '<':
          if log.is_init and is_event(log.mtd): log = None

        if isinstance(log, CallBase):
          util.mk_or_append(self._decls, log.cls, log.mtd)

        if log: self._logs.append(log)

    # indexing object appearances
    def wrap_obj(val):
      if '@' not in val: return val
      typ_w_pkg, hsh = val.split('@')
      _, typ, _ = util.explode_mname(typ_w_pkg + ".<init>")

      # regard the type's <init> is used at the least
      if typ not in self._decls:
        self._decls[typ] = []

      if typ in self._objs:
        if hsh in self._objs[typ]:
          idx = self._objs[typ].index(hsh)
        else: # first appearance of this hash
          idx = len(self._objs[typ])
          self._objs[typ].append(hsh)
      else: # first obj of this typ
        idx = 0
        self._objs[typ] = [hsh]
      return u"@Object(typ={}, idx={})".format(typ, idx)

    for log in self._logs:
      log.vals = map(wrap_obj, log.vals)

    self._num_objs = reduce(lambda acc, hshs: acc + len(hshs), self._objs.values(), 0)

  def __str__(self):
    return '\n'.join(map(str, self._logs))

  @property
  def name(self):
    return self._name

  @property
  def logs(self):
    return self._logs

  @property
  def decls(self):
    return self._decls

  @property
  def objs(self):
    return self._objs

  @property
  def num_objs(self):
    return self._num_objs

  @property
  def IOs(self):
    ios, _ = util.partition(lambda s: isinstance(s, CallBase), self._logs)
    return ios

  @property
  def evts(self):
    _, evts = util.partition(lambda s: isinstance(s, CallBase), self._logs)
    return evts

  @property
  def evt_kinds(self):
    kinds = map(op.attrgetter("kind"), self.evts)
    return util.rm_dup(kinds)

  @property
  def evt_sources(self):
    srcss = map(op.attrgetter("sources"), self.evts)
    return util.rm_dup(util.flatten(srcss))

  @takes("Sample", str, callable)
  @returns(list_of(object))
  def find(self, what, cond):
    cond_ed = filter(cond, self._logs)
    return map(op.attrgetter(what), cond_ed)



# a higher-order function that calculates the max number of something
def max_smpls(smpls, f):
  if not smpls: return 0
  def f_len(smpl): return len(f(smpl))
  return max(map(f_len, smpls))


# max length of call sequences amongst the given samples
@takes(list_of(Sample))
@returns(int)
def max_IOs(smpls):
  return max_smpls(smpls, op.attrgetter("IOs"))


# max length of input events amongst the given samples
@takes(list_of(Sample))
@returns(int)
def max_evts(smpls):
  return max_smpls(smpls, op.attrgetter("evts"))


# max number of object instances in the given samples
@takes(list_of(Sample))
@returns(int)
def max_objs(smpls):
  return max(map(op.attrgetter("num_objs"), smpls))


# a high-order function that applies the given function to all the samples
@takes(list_of(Sample), callable)
@returns(list_of(anything))
def map_smpls(smpls, f):
  return util.flatten(map(f, smpls))


# a high-order function that retrieves the given attribute all over the samples
@takes(list_of(Sample), callable)
@returns(list_of(anything))
def map_attr(smpls, f):
  return map_smpls(smpls, op.attrgetter(f.__name__))


# retrieve event kinds that appear in the samples
@takes(list_of(Sample))
@returns(list_of(unicode))
def evt_kinds(smpls):
  return util.rm_dup(map_attr(smpls, evt_kinds))


# retrieve (potential) sources of events in the samples
@takes(list_of(Sample))
@returns(list_of(unicode))
def evt_sources(smpls):
  return util.rm_dup(map_attr(smpls, evt_sources))


# collect all the class and method declarations in the samples
_decls = {} # { cls1 : [mtd1, mtd2, ...], cls2 : [...], ... }
def reset():
  global _decls
  _decls = {}


@takes(list_of(Sample))
@returns(dict_of(unicode, list_of(unicode)))
def decls(smpls):
  global _decls
  if not _decls:
    declss = map(op.attrgetter("decls"), smpls)
    _decls = util.merge_dict(declss)
  return _decls


# check whether the given method appears in the samples
# should consider class hierarchy
# e.g., Activity.on* won't appear, but subclasses' on* can
# thus, need classes of interest in an hierarchy
@takes(list_of(Sample), list_of("Clazz"), unicode)
@returns(bool)
def mtd_appears(smpls, clss, mname):
  _decls = decls(smpls)
  @takes("Clazz")
  @returns(bool)
  def cls_appears(cls):
    return cls.name in _decls and mname in _decls[cls.name]
  return any(filter(cls_appears, clss))


@takes(list_of(Sample))
@returns(dict_of(unicode, list_of(unicode)))
def objs(smpls):
  objss = map(op.attrgetter("objs"), smpls)
  return util.merge_dict(objss)


# find "what" attribute under certain conditions in the samples
@takes(list_of(Sample), str, callable)
@returns(set)
def find(smpls, what, cond):
  lst = map(op.methodcaller("find", what, cond), smpls)
  return set(util.flatten(lst))


# value's type
# 3.141592654 -> double
@takes(unicode)
def kind(val):
  try:
    if val == C.J.N: v_typ = C.J.OBJ
    else: v_typ = type(ast.literal_eval(val))
  except SyntaxError: # @Object(typ=..., )
    if '@' in val: return val
    else: v_typ = str
  except ValueError:
    if val in [C.J.T, C.J.F]: v_typ = bool
    else: v_typ = str
  return v_typ


# True if the given value is kind of the given type
jv2py = { C.J.z: bool, C.J.i: int, C.J.j: long, \
    C.J.f: float, C.J.d: float, C.J.STR: unicode }
@takes(unicode, unicode)
@returns(bool)
def eq_kind(typ, val):
  v_typ = kind(val)
  global jv2py
  try: return jv2py[typ] == v_typ
  except KeyError:
    try: return typ in v_typ
    except TypeError: return False


# find methods that return the designated types
@takes(list_of(Sample), list_of(unicode))
@returns(set)
def find_mtds_ext_typs(smpls, typs):
  # < ...(typ@...)
  def f_ext_typs(log):
    if isinstance(log, CallExt):
      # True if return value is one of the given types
      return any([v for v in log.vals for t in typs if eq_kind(t, v)])
    else: return False
  return find(smpls, "mtd", f_ext_typs)


# find a proper getter name (default: get + Fname)
@takes(list_of(Sample), list_of(unicode), unicode, optional(str))
@returns(unicode)
def find_getter(smpls, typs, Fname, prefix="get"):
  mtds_ext_typs = find_mtds_ext_typs(smpls, typs)
  mtds_w_fname = filter(lambda mtd: Fname in mtd, mtds_ext_typs)
  mtds = filter(lambda mtd: not util.is_class_name(mtd), mtds_w_fname)
  if any(mtds): return mtds.pop()
  else: return prefix + Fname


# find methods that recieve the designated types
@takes(list_of(Sample), list_of(unicode))
@returns(set)
def find_mtds_ent_typs(smpls, typs):
  # > ...(typ@...)
  def f_ent_typs(log):
    if isinstance(log, CallEnt):
      # True if parameters have all of the given types
      return cmp(typs, [t for t in typs for v in log.vals if eq_kind(t, v)]) == 0
    else: return False
  return find(smpls, "mtd", f_ent_typs)


# find a proper setter name (default: set + Fname)
@takes(list_of(Sample), list_of(unicode), unicode)
@returns(unicode)
def find_setter(smpls, typs, Fname):
  mtds_ent_typs = find_mtds_ent_typs(smpls, typs)
  mtds_w_fname = filter(lambda mtd: Fname in mtd, mtds_ent_typs)
  mtds = filter(lambda mtd: not util.is_class_name(mtd), mtds_w_fname)
  if any(mtds): return mtds.pop()
  else: return "set" + Fname


"""
To import lib.*, run as follows:
  pasket $ python -m pasket.sample
"""
if __name__ == "__main__":
  from optparse import OptionParser
  usage = "usage: python -m pasket.sample (sample.txt | sample_folder)+ [opt]"
  parser = OptionParser(usage=usage)
  parser.add_option("-m", "--method",
    action="store_true", dest="method", default=False,
    help="print occurred method names")
  parser.add_option("-e", "--event",
    action="store_true", dest="event", default=False,
    help="print occurred events")
  parser.add_option("-o", "--object",
    action="store_true", dest="obj", default=False,
    help="print occurred objects")

  (opt, argv) = parser.parse_args()

  if len(argv) < 1:
    parser.error("incorrect number of arguments")

  pwd = os.path.dirname(__file__)
  root_dir = os.path.join(pwd, "..")
  sys.path.append(root_dir)

  ## logging configuration
  logging.config.fileConfig(os.path.join(pwd, "logging.conf"))
  logging.getLogger().setLevel(logging.DEBUG)

  smpl_files = []
  for arg in argv:
    smpl_files.extend(util.get_files_from_path(arg, "txt"))

  reset()
  smpls = []
  for fname in smpl_files:
    smpl = Sample(fname, lambda mname: mname.endswith("Event"))
    smpls.append(smpl)

  if opt.method:
    _decls = decls(smpls)
    for cname in _decls.keys():
      mnames = ", ".join(list(_decls[cname]))
      print "{}: {}".format(cname, mnames)

  if opt.event:
    _evts = util.flatten(map(op.attrgetter("evts"), smpls))
    for evt in _evts: print str(evt)

  if opt.obj:
    print "# max: {}\n".format(max_objs(smpls))
    _objs = objs(smpls)
    for cname in _objs.keys():
      instances = ", ".join(_objs[cname])
      print "{}: {}".format(cname, instances)

  if not sum([opt.method, opt.event, opt.obj]):
    for smpl in smpls:
      print "Sample: {}".format(smpl.name)
      print str(smpl)

