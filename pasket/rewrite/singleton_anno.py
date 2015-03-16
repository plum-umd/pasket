from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import util
from .. import sample
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression, to_expression

class Singleton(object):

  @classmethod
  def find_singleton(cls):
    return lambda anno: anno.by_name(C.A.SINGLE)

  def __init__(self, smpls):
    self._smpls = smpls

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  ## @Singleton
  ## class C { ... }
  ##   =>
  ## class C { ...
  ##   private C() { }                 // private constructor
  ##   private static C instance;      // singleton holder
  ##   public static C getInstance() { // retriever
  ##     if (instance == null) { instance = new C(); }
  ##     return instance;
  ##   }
  ## }
  def rewrite(self, cls):
    cname = cls.name
    logging.debug("reducing: @{} class {} {{ ... }}".format(C.A.SINGLE, cname))

    # make the constructor(s) *private*
    inits = cls.inits
    if not inits: inits = [cls.add_default_init()]
    for init in inits:
      if C.mod.PR not in init.mods: init.mods.append(C.mod.PR)
      # rip off *public* modifier, if exists
      try: init.mods.remove(C.mod.PB)
      except ValueError: pass

    Fname = cname
    fname = cname.lower()
    for mtd in cls.mtds:
      mname = mtd.name
      if mname.startswith("get") and mname.endswith(cname):
        Fname = mname.replace("get",'')
        fname = Fname[:1].lower() + Fname[1:]
        break

    # add a static field to hold the singleton instance
    holder = cls.fld_by_name(fname)
    if not holder:
      holder = Field(clazz=cls, mods=[C.mod.PR, C.mod.ST], typ=cname, name=fname)
      logging.debug("adding field {0}.{1} of type {0}".format(cname, fname))
      cls.add_flds([holder])

    # retriever
    mname = sample.find_getter(self._smpls, [cname], Fname)
    mtd_g = cls.mtd_by_sig(mname)
    if not mtd_g:
      mtd_g = Method(clazz=cls, mods=[C.mod.PB, C.mod.ST], typ=cname, name=mname)
      logging.debug("adding method {}.{}".format(cname, mname))
      cls.add_mtds([mtd_g])
    body = u"""
      if ({fname} == null) {{ {fname} = new {cname}(); }}
      return {fname};
    """.format(**locals())
    logging.debug("filling getter {}.{}".format(cname, mname))
    mtd_g.body = to_statements(mtd_g, body)

    # to replace annotation @Singleton(Class) in expressions
    setattr(cls, "singleton", holder)
    setattr(holder, "getter", mtd_g)

  @v.when(Template)
  def visit(self, node):
    for cls in node.classes:
      if util.exists(Singleton.find_singleton(), cls.annos):
        self.rewrite(cls)

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  ## @Singleton(C) => C.getInstance()
  @v.when(Expression)
  def visit(self, node):
    if node.kind == C.E.ANNO:
      _anno = node.anno
      if _anno.name == C.A.SINGLE:
        logging.debug("reducing: {}".format(str(_anno)))
        cls_s = class_lookup(_anno.cid)
        mtd_g = cls_s.singleton.getter
        return to_expression(u"{}.{}()".format(cls_s.name, mtd_g.name))

    return node

