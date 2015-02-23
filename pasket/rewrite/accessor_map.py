import operator as op
from itertools import product
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
    mtds = AccessorMap.get_candidate_mtds(cls)
    return cls.is_class and any(mtds)

  @staticmethod
  def is_candidate_getter(mtd):
    return not mtd.is_init and not mtd.is_static and \
        len(mtd.params) == 1 and mtd.typ != C.J.v

  @staticmethod
  def is_candidate_setter(mtd):
    return not mtd.is_init and not mtd.is_static and \
        len(mtd.params) == 2 and mtd.typ == C.J.v

  @staticmethod
  def is_candidate_mtd(mtd):
    return AccessorMap.is_candidate_getter(mtd) or AccessorMap.is_candidate_setter(mtd)

  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(AccessorMap.get_candidate_mtds, cls.subs))
    return filter(AccessorMap.is_candidate_mtd, mtds)

  ##
  ## generate an aux type for getter/setter
  ##
  def gen_aux_cls(self, conf, tmpl):
    aux = Clazz(name=self.aux_name, mods=[C.mod.PB], subs=self._clss)
    self.aux = aux
    tmpl.acc_auxs.append(self.aux_name)

    rv_accs = map(lambda c: '_'.join([C.ACC.ACC, c]), conf.iterkeys())

    def get_g_roles(name, c):
      return map(lambda n: '_'.join([name, c, str(n)]), range(conf[c][1]))
    def get_s_roles(name, c):
      return map(lambda n: '_'.join([name, c, str(n)]), range(conf[c][2]))

    rv_gtts = util.flatten(map(partial(get_g_roles, C.ACC.GET), conf.iterkeys()))
    rv_stts = util.flatten(map(partial(get_s_roles, C.ACC.SET), conf.iterkeys()))
    gs_vars = util.flatten(map(partial(get_g_roles, C.ACC.GS), conf.iterkeys()))

    # set role variables
    def set_role(role):
      setattr(aux, role, '_'.join([role, aux.name]))
    map(set_role, rv_accs)
    map(set_role, rv_gtts)
    map(set_role, rv_stts)
    map(set_role, gs_vars)

    # add fields that stand for non-deterministic role choices
    def aux_fld(init, ty, nm):
      if hasattr(aux, nm): nm = getattr(aux, nm)
      return Field(clazz=aux, mods=[C.mod.ST], typ=ty, name=nm, init=init)
    hole = to_expression(C.T.HOLE)
    aux_int = partial(aux_fld, hole, C.J.i)

    aux.add_flds(map(aux_int, gs_vars))

    c_to_e = lambda c: to_expression(unicode(c))

    ## range check
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRange")
    checkers = []
    gen_range = lambda ids: gen_E_gen(map(c_to_e, ids))
    get_id = op.attrgetter("id")

    # range check for accessors
    cls_ids = map(get_id, self._clss)
    cls_init = gen_range(cls_ids)
    aux_int_cls = partial(aux_fld, cls_init, C.J.i)
    aux.add_flds(map(aux_int_cls, rv_accs))

    # range check for getter/setter
    mtds = util.flatten(map(AccessorMap.get_candidate_mtds, self._clss))

    def aux_range(rl, c, nm, mtds, num_args, is_void):
      ids = map(get_id, filter(lambda m: len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds))
      init = gen_range(ids)
      role = getattr(aux, '_'.join(map(str, [rl, c, nm])))
      aux.add_flds([aux_fld(init, C.J.i, role)])

    def mtd_range(c):
      map(lambda m: [aux_range(C.ACC.GET, c, m, mtds, 1, False)], range(conf[c][1]))
      map(lambda m: [aux_range(C.ACC.SET, c, m, mtds, 2, True)], range(conf[c][2]))
    map(mtd_range, conf.iterkeys())

    # other semantics checks
    # such as ownership, bundle getter/setter, and signature types
    def owner_range(rl, c, ids):
      return map(lambda i: "assert subcls("+getattr(aux, '_'.join([C.ACC.ACC, c]))+", belongsTo("+getattr(aux, '_'.join([rl, c, str(i)]))+"));", ids)
    for c in conf.iterkeys():
      checkers.extend(owner_range(C.ACC.GET, c, range(conf[c][1])))
      checkers.extend(owner_range(C.ACC.SET, c, range(conf[c][2])))

    def bundle_getter_setter(c, gids, sids):
      return map(lambda (g, s): "assert belongsTo("+getattr(aux, '_'.join([C.ACC.GET, c, str(g)])) + ") == belongsTo(" + getattr(aux, '_'.join([C.ACC.SET, c, str(s)])) + ");", product(gids, sids))
    for c in conf.iterkeys():
      checkers.extend(bundle_getter_setter(c, range(conf[c][1]), range(conf[c][2])))

    def getter_sig(c):
      return map(lambda i: "assert (argNum(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)])) + ")) == 1;", range(conf[c][1]))
    def setter_sig(c):
      return map(lambda i: "assert (argNum(" + getattr(aux, '_'.join([C.ACC.SET, c, str(i)])) + ")) == 2;", range(conf[c][2]))
    def gs_match(c):
      return map(lambda i: "assert subcls(argType(" + getattr(aux, '_'.join([C.ACC.SET, c, str(i)]))+", 1), retType(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)])) + "));", range(conf[c][2]))
    checkers.extend(reduce(lambda x,y: x+y, map(getter_sig, conf.iterkeys())))
    checkers.extend(reduce(lambda x,y: x+y, map(setter_sig, conf.iterkeys())))
    checkers.extend(reduce(lambda x,y: x+y, map(gs_match, conf.iterkeys())))

    rg_chk.body += to_statements(rg_chk, '\n'.join(checkers))
    aux.add_mtds([rg_chk])

    add_artifacts([aux.name])
    return aux


  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)
    aux = self.gen_aux_cls(self._acc_conf, node)
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

