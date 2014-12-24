import copy as cp
from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import util
from .. import sample
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
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
    cls_p = Clazz.lookup(proxy)

    cname = node.name
    logging.debug("reducing: @{}({}) class {}".format(C.A.PROXY, proxy, cname))

    # introduce a field to hold the proxy instance: P _proxy
    fld = Field(clazz=node, typ=proxy, name=u"_proxy")
    node.add_flds([fld])

    # add methods that delegate desired operations to the proxy
    for mtd in cls_p.mtds:
      mname = mtd.name
      mtd_p = cp.deepcopy(mtd)
      mtd_p.clazz = node
      if mtd.name != mtd.typ: # to avoid constructor
        args = ", ".join(map(lambda (_, nm): nm, mtd.params))
        body = "_proxy.{mname}({args});".format(**locals())
        if mtd.typ is not C.J.v: body = "return " + body
      else: # cls' own <init>: cname(P p) { _proxy = p; }
        mtd_p.typ = mtd_p.name = cname
        mtd_p.params = [ (proxy, u"x") ]
        body = "_proxy = x;"
      mtd_p.body = to_statements(mtd_p, body)
      node.add_mtds([mtd_p])

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

