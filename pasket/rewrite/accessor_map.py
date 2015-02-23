import logging

import lib.const as C
import lib.visit as v

from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression

class AccessorMap(object):

  def __init__(self, smpls, acc_default, acc_conf):
    self._smpls = smpls
    self._acc_default = acc_default
    self._acc_conf = acc_conf

    self._clss = []
    self._aux_name = C.ACC.AUX+"Map"
    self._aux = None

  @property
  def aux_name(self):
    return self._aux_name

  @property
  def aux(self):
    return self._aux

  @aux.setter
  def aux(self, v):
    self._aux = v

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  # find candidate classes that have candidate getter/setter of Map type
  def find_clss_involved(self, tmpl):
    clss = util.flatten_classes(tmpl.classes, "inners")
    self._clss = filter(AccessorMap.is_candidate_cls, clss)
    logging.debug("{} candidates: {}".format(self._aux_name, self._clss))

  @staticmethod
  def is_candidate_cls(cls):
    mtds = filter(lambda m: not m.is_init and not m.is_static, cls.mtds)
    getters = filter(lambda m: len(m.params) == 1 and m.typ != C.J.v, mtds)
    setters = filter(lambda m: len(m.params) == 2, mtds)
    return cls.is_class and (any(getters) or any(setters))

  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)

  @v.when(Clazz)
  def visit(self, node): pass

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

