import logging

import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement
from ..meta.expression import Expression

class Singleton(object):

  def __init__(self, smpls):
    self._smpls = smpls

    self._clss = []
    self._aux_name = C.SNG.AUX
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

  # find candidate classes that have candidate getter
  def find_clss_involved(self, tmpl):
    clss = util.flatten_classes(tmpl.classes, "inners")
    self._clss = filter(Singleton.is_candidate_cls, clss)
    logging.debug("{} candidates: {}".format(self._aux_name, self._clss))

  @staticmethod
  def is_candidate_cls(cls):
    mtds = Singleton.get_candidate_mtds(cls)
    return cls.is_class and any(mtds)

  @staticmethod
  def is_candidate_mtd(mtd):
    return not mtd.is_init and mtd.is_static and \
        len(mtd.params) == 0 and mtd.typ == mtd.clazz.name

  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(Singleton.get_candidate_mtds, cls.subs))
    return filter(Singleton.is_candidate_mtd, mtds)

  @staticmethod
  def add_fld(cls, ty, nm):
    logging.debug("adding field {}.{} of type {}".format(cls.name, nm, ty))
    fld = Field(clazz=cls, typ=ty, name=nm)
    cls.add_flds([fld])
    return fld

  ##
  ## generate an aux type
  ##
  def gen_aux_cls(self, tmpl):
    aux = Clazz(name=self._aux_name, mods=[C.mod.PB], subs=self._clss)
    self.aux = aux
    tmpl.sng_auxs.append(self.aux_name)

    add_artifacts([aux.name])
    return aux

  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)
    aux = self.gen_aux_cls(node)
    node.add_classes([aux])

  @v.when(Clazz)
  def visit(self, node):
    if node.name == C.J.OBJ:
      Singleton.add_fld(node, C.J.OBJ, C.SNG.INS)

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node): pass

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

