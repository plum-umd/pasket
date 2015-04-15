#!/usr/bin/env python

import cStringIO
from itertools import ifilter
from functools import partial
import logging
import operator as op
import os
import sys

from antlr3.tree import CommonTree as AST

from lib.typecheck import *
import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from ..anno import parse_anno

from . import fields_reset, methods_reset, classes_reset, fields, methods, classes, class_lookup
import statement as st
from field import Field
from method import Method
from clazz import Clazz, parse_class, merge_layer, find_base

class Template(v.BaseNode):

  def __init__(self, ast):
    # reset ids and lists of meta-classes: Field, Method, and Clazz

    fields_reset()
    methods_reset()
    classes_reset()
    self._frozen = False

    # class declarations in this template
    self._classes = [] # [ Clazz... ]
    # event involved in this template
    self._events = {} # [ event_kind0 : 0, ... ]
    self._evt_annotated = False
    # aux types for observer patterns
    self._obs_auxs = {} # { Aux...1 : [ C1, D1 ], ... }
    # aux types for accessor patterns
    self._acc_auxs = [] # [ Aux...1, ... ]

    # primitive classes
    cls_obj = Clazz(pkg=u"java.lang", name=C.J.OBJ)
    cls_obj.sup = None # Object is the root
    self._classes.append(cls_obj)

    find_obs = lambda anno: anno.by_name(C.A.OBS)
    annos = []
    pkg = None
    mods = []
    events = []
    for _ast in ast.getChildren():
      tag = _ast.getText()
      if tag in [C.T.CLS, C.T.ITF, C.T.ENUM]:
        clazz = parse_class(_ast)
        clazz.annos = annos
        if pkg: clazz.pkg = pkg
        clazz.mods = mods
        self._classes.append(clazz)

        # collect event kinds
        for cls in util.flatten_classes([clazz], "inners"):
          # 1) class itself is sort of event
          if cls.is_event:
            events.append(repr(cls))
          # 2) might be annotated with explicit event sorts
          elif util.exists(find_obs, annos):
            _anno = util.find(find_obs, annos)
            events.extend(_anno.events)
            self._evt_annotated = True

        annos = []
        pkg = None
        mods = []

      elif tag == C.T.ANNO:
        annos.append(parse_anno(_ast))
      elif tag == C.T.PKG:
        p_node = util.mk_v_node_w_children(_ast.getChildren())
        pkg = util.implode_id(p_node)
      else: # modifiers
        mods.append(tag)
    ## parsing done
    ## post manipulations go below

    logging.debug("# class(es): {}".format(len(classes())))
    logging.debug("# method(s): {}".format(len(methods())))
    logging.debug("# field(s): {}".format(len(fields())))

    self.consist()

    # remove duplicates in events
    events = util.rm_dup(events)
    if events:
      logging.debug("event(s) in the template: {}: {}".format(len(events), events))
      # numbering the event kinds
      for i, event in enumerate(events):
        self._events[event] = i

    # if there exists java.util.EventObject (i.e., cmd == "gui")
    # no additional class is required to represent events
    evt_obj = class_lookup(C.GUI.EVT)
    if evt_obj:
      fld = Field(clazz=evt_obj, mods=[C.mod.PB], typ=C.J.i, name=u"kind")
      evt_obj.flds.append(fld)

    # o.w. introduce artificial class Event that implodes all event kinds
    # class Event { int kind; E_kind$n$ evt$n$; }
    elif events:
      cls_e = merge_layer(u"Event", map(class_lookup, events))
      cls_e.add_default_init()
      self._classes.append(cls_e)
      add_artifacts([u"Event"])

  # keep snapshots of instances of meta-classes
  def freeze(self):
    self._flds = fields()
    self._mtds = methods()
    self._clss = classes()

  # restore snapshots of instances of meta-classes
  def unfreeze(self):
    fields_reset(self._flds)
    methods_reset(self._mtds)
    classes_reset(self._clss)

  @property
  def classes(self):
    return self._classes

  @classes.setter
  def classes(self, v):
    self._classes = v
    
  def add_classes(self, v):
    self._classes.extend(v)
  
  @property
  def events(self):
    return self._events

  @events.setter
  def events(self, v):
    self._events = v

  @property
  def is_event_annotated(self):
    return self._evt_annotated

  @property
  def obs_auxs(self):
    return self._obs_auxs
  
  @obs_auxs.setter
  def obs_auxs(self, v):
    self._obs_auxs = v
 
  @property
  def acc_auxs(self):
    return self._acc_auxs

  @acc_auxs.setter
  def acc_auxs(self, v):
    self._acc_auxs = v

  def __str__(self):
    return '\n'.join(map(str, self._classes))

  def accept(self, visitor):
    visitor.visit(self)
    clss = util.flatten_classes(self._classes, "inners")
    map(op.methodcaller("accept", visitor), clss)

  # to make the template type-consistent
  #   collect all the types in the template
  #   build class hierarchy
  #   discard interfaces without implementers
  #   discard methods that refer to undefined types
  def consist(self):
    clss = util.flatten_classes(self._classes, "inners")

    # collect *all* types in the template
    # including inners as well as what appear at field/method declarations
    # (since we don't care about accessability, just flatten inner classes)
  
    # for easier(?) membership test
    # { cls!r: Clazz(cname, ...), ... }
    decls = { repr(cls): cls for cls in clss }

    def add_decl(tname):
      # (not) to handle primitive types, such as int
      # if not util.is_class_name(tname): return
      if tname in decls: return
      cls = Clazz(name=tname)
      decls[tname] = cls
      # add declarations in nested generics
      if util.is_collection(tname):
        map(add_decl, util.of_collection(tname)[1:])

    # finding types that occur at field/method declarations
    for cls in clss:
      for fld in cls.flds:
        if fld.typ not in decls: add_decl(fld.typ)
      for mtd in cls.mtds:
        for (ty, nm) in mtd.params:
          if ty not in decls: add_decl(ty)

    # build class hierarchy: fill Clazz.subs
    for cls in clss:
      if not cls.sup and not cls.itfs: continue
      sups = map(util.sanitize_ty, cls.itfs)
      if cls.sup: sups.append(util.sanitize_ty(cls.sup))
      for sup in clss:
        sname = repr(sup)
        if sname in sups:
          if cls not in sup.subs: sup.subs.append(cls)

    # discard interfaces that have no implementers, without constants
    for itf in ifilter(op.attrgetter("is_itf"), clss):
      if not itf.subs and not itf.flds:
        logging.debug("discarding {} with no implementers".format(itf.name))
        self._classes.remove(itf) # TODO: ValueError raised if itf is inner
        del decls[repr(itf)]

    # some interfaces might have been discarded, hence retrieve classes again
    clss = util.flatten_classes(self._classes, "inners")

    # discard methods that refer to undefined types
    for cls in clss:
      for mtd in cls.mtds[:]: # to remove items, should use a shallow copy
        def undefined_type( (ty, _) ): return ty not in decls
        if util.exists(undefined_type, mtd.params):
          ty, _ = util.find(undefined_type, mtd.params)
          logging.debug("discarding {} due to lack of {}".format(mtd.name, ty))
          cls.mtds.remove(mtd)

  # invoke Clazz.mtds_w_anno for all classes
  @takes("Template", callable)
  @returns(list_of(Method))
  def mtds_w_anno(self, cmp_anno):
    mtdss = map(lambda cls: cls.mtds_w_anno(cmp_anno), self._classes)
    return util.ffilter(util.flatten(mtdss))

  # find methods with @Harness
  # if called with a specific name, will returns the exact method
  @takes("Template", optional(str))
  @returns( (list_of(Method), Method) )
  def harness(self, name=None):
    if name:
      h_finder = lambda anno: anno.by_attr({"name": C.A.HARNESS, "f": name})
    else:
      h_finder = lambda anno: anno.by_name(C.A.HARNESS)
    mtds = self.mtds_w_anno(h_finder)
    if mtds and name: return mtds[0]
    else: return mtds

  # find main()
  @property
  def main(self):
    mtds = []
    # assume *main* is not defined in inner classes
    for cls in self._classes:
      for mtd in cls.mtds:
        if C.mod.ST in mtd.mods and mtd.name == C.J.MAIN:
          mtds.append(mtd)
    n = len(mtds)
    if n > 1:
      raise Exception("multiple main()s", mtds)
    elif 1 == n: return mtds[0]
    else: return None

  # find the class to which main() belongs
  @property
  def main_cls(self):
    main = self.main
    harness = self.harness()
    if main: return main.clazz
    # assume @Harness methods are defined at the same class
    elif harness: return harness[0].clazz
    else: raise Exception("None of main() and @Harness is found")

  # add main() that invokes @Harness methods
  @takes("Template")
  @returns(nothing)
  def add_main(self):
    main_cls = self.main_cls
    if any(main_cls.mtd_by_name(u"main")): return
    params = [ (u"String[]", u"args") ]
    main = Method(clazz=main_cls, mods=C.PBST, name=u"main", params=params)
    def to_call(mtd): return mtd.name + "();"
    body = '\n'.join(map(to_call, self.harness()))
    main.body = st.to_statements(main, body)
    main_cls.mtds.append(main)


"""
To import lib.*, run as follows:
  pasket $ python -m spec.meta.template
"""
if __name__ == "__main__":
  from optparse import OptionParser
  usage = "usage: python -m spec.meta.template (template.java | template_folder)+ [opt]"
  parser = OptionParser(usage=usage)
  parser.add_option("--hierarchy",
    action="store_true", dest="hierarchy", default=False,
    help="print inheritance hierarchy")
  parser.add_option("--method",
    action="store_true", dest="method", default=False,
    help="print declared methods in the template")
  parser.add_option("-e", "--event",
    action="store_true", dest="event", default=False,
    help="print event sorts in the template(s)")

  (opt, argv) = parser.parse_args()

  if len(argv) < 1:
    parser.error("incorrect number of arguments")

  pwd = os.path.dirname(__file__)
  src_dir = os.path.join(pwd, "..")
  root_dir = os.path.join(src_dir, "..")
  sys.path.append(root_dir)

  ## logging configuration
  logging.config.fileConfig(os.path.join(src_dir, "logging.conf"))
  logging.getLogger().setLevel(logging.DEBUG)

  tmpl_files = []
  for arg in argv:
    tmpl_files.extend(util.get_files_from_path(arg, "java"))

  ast = util.toAST(tmpl_files)
  tmpl = Template(ast)

  if opt.hierarchy:

    def toStringTree(cls, depth=0):
      buf = cStringIO.StringIO()
      buf.write("%*s" % (depth, ""))
      if cls.is_class: buf.write("[c] ")
      elif cls.is_itf: buf.write("[i] ")
      elif cls.is_enum: buf.write("[e] ")
      buf.write(repr(cls))
      if cls.itfs: buf.write(" : " + ", ".join(map(str, cls.itfs)))
      buf.write('\n')
      for sub in cls.subs:
        buf.write(toStringTree(sub, depth+2))
      return buf.getvalue()

    tmpl.consist()
    bases = util.rm_dup(map(find_base, classes()))
    for cls in bases:
      print toStringTree(cls, 0)

  if opt.method:
    for mtd in methods():
      print mtd.signature

  if opt.event:
    for evt in tmpl.events:
      print evt

  if not sum([opt.hierarchy, opt.method, opt.event]):
    print str(tmpl)

