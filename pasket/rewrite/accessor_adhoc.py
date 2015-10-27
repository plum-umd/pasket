import operator as op
import logging

import lib.const as C
import lib.visit as v

from .. import util
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz, find_mtds_by_sig
from ..meta.method import Method, sig_match
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression

class AccessorAdHoc(object):
  def __init__(self, smpls, acc_default=[]):
    self._smpls = smpls
    self._acc_default = acc_default

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Template)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node):
    name = node.name
    if name in C.J.OBJ: pass
    elif not node.is_class: pass
    elif node.is_anony: pass
    elif node.has_init: pass
    else:
      sup = node.in_hierarchy(op.attrgetter("has_init"))
      if sup: # if superclass has <init>
        for sup_mtd in sup.inits:
          params = sup_mtd.params
          mtd = Method(clazz=node, mods=[C.mod.PB], typ=name, name=name, params=sup_mtd.params)
          node.mtds.append(mtd)
          typs, _ = util.split(params)
          logging.debug("adding {}.<init>({})".format(name, ", ".join(typs)))
      elif node.flds:
        node.add_fld_init()
        logging.debug("adding {}.<init>: field initializer".format(name))
      else:
        node.add_default_init()
        logging.debug("adding {}.<init>: default".format(name))

  @v.when(Field)
  def visit(self, node): pass

  verbs = ["get", "my", "is", "has", "set"]

  @staticmethod
  def is_accessor(mname):
    for v in AccessorAdHoc.verbs:
      if mname.startswith(v): return True
    return False

  @staticmethod
  def get_fname(mname):
    def rm_verb(acc, v): return acc.replace(v, '')
    fname = reduce(lambda acc, v: rm_verb(acc, v), AccessorAdHoc.verbs, mname)
    return '_' + fname.lower()

  @staticmethod
  def add_fld(cls, ty, nm):
    logging.debug("adding field {}.{} of type {}".format(cls.name, nm, ty))
    fld = Field(clazz=cls, typ=ty, name=nm)
    cls.add_flds([fld])
    cls.init_fld(fld)
    return fld

  @v.when(Method)
  def visit(self, node):
    # skip the method with explicit annotations, e.g., @Factory
    if node.annos: return
    # skip java.lang.*
    if node.clazz.pkg in ["java.lang"]: return
    # can't edit interface's methods or abstract methods
    if node.clazz.is_itf or node.is_abstract: return
    # can't edit client side
    if node.clazz.client: return
    # skip instance methods which have (hand-written) body
    if not node.is_init and node.body: return

    mname = node.name
    sig = ", ".join(node.param_typs)
    cls = node.clazz

    ##
    ## add super() into <init>
    ## 1) if it has an approriate super class
    ## 2)     and does not have super()
    ##
    if node.is_init and cls.sup and cls.sup != C.J.OBJ and \
        (not node.body or not str(node.body[0]).startswith(C.J.SUP)):
      sup_inits = find_mtds_by_sig(cls.sup, cls.sup, node.param_typs)
      if sup_inits: # sig-matched super()
        if 1 == len(sup_inits):
          args = sig_match(sup_inits[0].params, node.params)
        else: raise Exception("<init>s with same signature: {}".format(sup_inits))
      else: # try other super(...)
        sup = class_lookup(cls.sup)
        args = []
        for mtd in sup.inits:
          _args = sig_match(mtd.params, node.params)
          if len(args) < len(_args): args = _args

      sup_call = u"super({});".format(", ".join(args))
      logging.debug("adding {} into {}({})".format(sup_call, cls.name, sig))
      node.body = to_statements(node, sup_call) + node.body

    body = []

    ##
    ## fill <init> with field initializers
    ## NOTE: deprecated (use constructor pattern)
    ##
    if node.is_init and node.params and False:
      logging.debug("filling {}({})".format(cls.name, sig))
      flds = []
      for ty, nm in node.params:
        fname = AccessorAdHoc.get_fname(nm)
        if cls.fld_by_name(fname): continue
        if not cls.sup or not class_lookup(cls.sup).fld_by_name(fname):
          fld = AccessorAdHoc.add_fld(cls, ty, fname)
          flds.append(fld)

      def to_virtual_param(fld): return (fld.typ, fld.name)
      virtual_params = map(to_virtual_param, flds)
      args = sig_match(virtual_params, node.params)
      for fld, arg in zip(flds, args):
        body.append("{} = {};".format(fld.name, arg))

    ##
    ## getters and setters
    ##
    elif not node.is_static and AccessorAdHoc.is_accessor(mname) and \
        (not self._acc_default or \
            cls.name in self._acc_default or mname in self._acc_default):

      fname = AccessorAdHoc.get_fname(mname)

      ## getters
      ##
      ## typ getX();
      ##   =>
      ## typ getX() { return x; }
      if util.exists(lambda verb: mname.startswith(verb), ["get", "is", "my"]):
        logging.debug("filling getter: {}.{}".format(cls.name, mname))
        fld = cls.fld_by_name(fname)
        if not fld: fld = AccessorAdHoc.add_fld(cls, node.typ, fname)
        setattr(fld, "getter", node)
        body.append(u"return {};".format(fname))

      elif mname.startswith("has"): pass

      ## setters
      ##
      ## void setX(typ x);
      ##   =>
      ## void setX(typ x) { _x = x; }
      elif mname.startswith("set") and 1 == len(node.params):
        logging.debug("filling setter: {}.{}".format(cls.name, mname))
        ty, nm = node.params[0]
        fld = cls.fld_by_name(fname)
        if not fld: fld = AccessorAdHoc.add_fld(cls, ty, fname)
        setattr(fld, "setter", node)
        body.append(u"{} = {};".format(fname, nm))

    if body:
      logging.debug(u'\n'.join(body))
      node.body += to_statements(node, u'\n'.join(body))

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

