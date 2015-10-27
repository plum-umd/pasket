import copy as cp
import logging

import lib.const as C
import lib.visit as v

from .. import util
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression

class Proxy(object):

  @classmethod
  def find_proxy(cls):
    return lambda anno: anno.by_name(C.A.PROXY)

  def __init__(self, smpls):
    self._smpls = smpls

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Template)
  def visit(self, node): pass

  ## @Proxy(P)
  ## class C { }
  ##   =>
  ## class C {
  ##   P _proxy;
  ##   C(P p) { _proxy = p; }
  ##   m$i$(...) { _proxy.m$i$(...); }
  ## }
  @v.when(Clazz)
  def visit(self, node):
    if not util.exists(Proxy.find_proxy(), node.annos): return

    _anno = util.find(Proxy.find_proxy(), node.annos)
    if hasattr(_anno, "cid"): proxy = _anno.cid
    elif len(node.sups) == 1: proxy = node.sups[0]
    else: raise Exception("ambiguous proxy", _anno)

    cname = node.name
    logging.debug("reducing: @{}({}) class {}".format(C.A.PROXY, proxy, cname))

    cls_p = class_lookup(proxy)
    setattr(node, "proxy", cls_p)

    # introduce a field to hold the proxy instance: P _proxy
    fld = Field(clazz=node, typ=proxy, name=u"_proxy")
    node.add_flds([fld])
    node.init_fld(fld)

    # if purely empty proxy
    # add methods that delegate desired operations to the proxy
    if not node.mtds:
      for mtd_p in cls_p.mtds:
        mname = mtd.name
        mtd_cp = cp.deepcopy(mtd_p)
        mtd_cp.clazz = node
        if not mtd_p.is_init:
          args = ", ".join(map(lambda (_, nm): nm, mtd_p.params))
          body = u"_proxy.{mname}({args});".format(**locals())
          if mtd_p.typ != C.J.v: body = u"return " + body
        else: # cls' own <init>: cname(P p) { _proxy = p; }
          mtd_cp.name = cname
          mtd_cp.typ = cname
          mtd_cp.params = [ (proxy, u"x") ]
          body = u"_proxy = x;"
        mtd_cp.body = to_statements(mtd_p, body)
        logging.debug("{} ~> {}".format(mtd_cp.signature, mtd_p.signature))
        node.add_mtds([mtd_cp])

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    if not hasattr(node.clazz, "proxy"): return

    cls_p = getattr(node.clazz, "proxy")
    mtd_p = cls_p.mtd_by_sig(node.name, node.param_typs)
    if mtd_p: # method delegation
      logging.debug("{} ~> {}".format(node.signature, mtd_p.signature))
      mname = node.name
      args = ", ".join(map(lambda (_, nm): nm, node.params))
      body = u"_proxy.{mname}({args});".format(**locals())
      if node.typ != C.J.v: body = u"return " + body
      node.body = to_statements(node, body)

    mname = node.name
    if mname.startswith("get") and mname.endswith(cls_p.name):
      body = u"return _proxy;"
      node.body = to_statements(node, body)

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

