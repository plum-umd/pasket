import logging

import lib.const as C
import lib.visit as v

from ...meta.template import Template
from ...meta.clazz import Clazz
from ...meta.method import Method
from ...meta.field import Field
from ...meta.statement import Statement, to_statements
from ...meta.expression import Expression

class Observer(object):

  @classmethod
  def find_obs(cls):
    return lambda anno: anno.by_name(C.A.OBS)

  # to avoid name conflict, use fresh counter as suffix
  __cnt = 0
  @classmethod
  def fresh_cnt(cls):
    cls.__cnt = cls.__cnt + 1
    return cls.__cnt

  @classmethod
  def new_aux(cls, suffix=None):
    if not suffix:
      suffix = str(Observer.fresh_cnt())
    return u"{}{}".format(C.OBS.AUX, suffix)

  def __init__(self, smpls):
    self._smpls = smpls

    self._cur_mtd = None

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  @v.when(Template)
  def visit(self, node): pass

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    self._cur_mtd = node

  @v.when(Statement)
  def visit(self, node): return [node]

  ## @React
  ##   =>
  ## Message m = q.next();
  ## Handler h = m.getTarget();
  ## h.dispatchMessage(m);
  # NOTE: assume @React is in @Harness only; and then use variable q there
  @v.when(Expression)
  def visit(self, node):
    if node.kind == C.E.ANNO:
      _anno = node.anno
      if _anno.name == C.A.REACT:
        logging.debug("reducing: {}".format(str(_anno)))

        suffix = Observer.fresh_cnt()
        body = u"""
          {1} msg{0} = q.next();
          {2} hdl{0} = msg{0}.getTarget();
          hdl{0}.dispatch{1}(msg{0});
        """.format(suffix, C.ADR.MSG, C.ADR.HDL)

        return to_statements(self._cur_mtd, body)

    return node

