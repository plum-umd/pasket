import operator as op
from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression, to_expression, gen_E_gen

class Singleton(object):

  def __init__(self, smpls, sng_conf=[]):
    self._smpls = smpls
    self._sng_conf = sng_conf

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

  def getter(self, aux):
    params = [ (C.J.i, u"mtd_id") ]
    getr = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=u"getInstance")
    # TODO: need to call candidate class's <init> nondeterministically
    rtn = u"""
      if ({0} == null) {{
        {0} = new Object();
      }}
      return {0};
    """.format(C.SNG.INS)
    getr.body = to_statements(getr, rtn)
    aux.add_mtds([getr])
    setattr(aux, "gttr", getr)

  @staticmethod
  def add_fld(cls, ty, nm):
    logging.debug("adding field {}.{} of type {}".format(cls.name, nm, ty))
    fld = Field(clazz=cls, mods=[C.mod.ST], typ=ty, name=nm)
    cls.add_flds([fld])
    return fld

  ##
  ## generate an aux type
  ##
  def gen_aux_cls(self, conf, tmpl):
    aux = Clazz(name=self._aux_name, mods=[C.mod.PB], subs=self._clss)
    self.aux = aux
    tmpl.sng_auxs.append(self.aux_name)

    rv_sngs = map(lambda c: '_'.join([C.SNG.SNG, c]), conf)
    rv_gtts = map(lambda c: '_'.join([C.SNG.GET, c]), conf)

    # set role variables
    def set_role(role):
      setattr(aux, role, '_'.join([role, aux.name]))
    map(set_role, rv_sngs)
    map(set_role, rv_gtts)

    # add fields that stand for non-deterministic role choices
    def aux_fld(init, ty, nm):
      if hasattr(aux, nm): nm = getattr(aux, nm)
      return Field(clazz=aux, mods=[C.mod.ST], typ=ty, name=nm, init=init)
    hole = to_expression(C.T.HOLE)
    aux_int = partial(aux_fld, hole, C.J.i)

    c_to_e = lambda c: to_expression(unicode(c))

    ## range check
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRange")
    checkers = []
    gen_range = lambda ids: gen_E_gen(map(c_to_e, ids))
    get_id = op.attrgetter("id")

    # range check for singleton classes
    cls_ids = map(get_id, self._clss)
    cls_init = gen_range(cls_ids)
    aux_int_cls = partial(aux_fld, cls_init, C.J.i)
    aux.add_flds(map(aux_int_cls, rv_sngs))

    # range check for getter
    mtds = util.flatten(map(Singleton.get_candidate_mtds, self._clss))

    mtd_ids = map(get_id, mtds)
    mtd_init = gen_range(mtd_ids)
    aux_int_mtd = partial(aux_fld, mtd_init, C.J.i)
    aux.add_flds(map(aux_int_mtd, rv_gtts))

    # other semantics checks
    # such as ownership and signature types
    def owner_range(c):
      return u"assert subcls("+getattr(aux, '_'.join([C.SNG.SNG, c]))+", belongsTo("+getattr(aux, '_'.join([C.SNG.GET, c]))+"));"
    checkers.extend(map(owner_range, conf))

    def getter_sig(c):
      return u"assert (argNum("+getattr(aux, '_'.join([C.SNG.GET, c]))+")) == 0;"
    checkers.extend(map(getter_sig, conf))

    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    ## a singleton holder
    Singleton.add_fld(aux, C.J.OBJ, C.SNG.INS)

    ## getter
    self.getter(aux)

    add_artifacts([aux.name])
    return aux

  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)
    aux = self.gen_aux_cls(self._sng_conf, node)
    node.add_classes([aux])

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

