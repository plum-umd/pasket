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
    return not mtd.is_init and len(mtd.params) == 1 and mtd.typ != C.J.v

  @staticmethod
  def is_candidate_setter(mtd):
    return not mtd.is_init and len(mtd.params) == 2 and mtd.typ == C.J.v \
        and util.is_class_name(mtd.param_typs[1]) # assume subtype of Object

  @staticmethod
  def is_candidate_mtd(mtd):
    return AccessorMap.is_candidate_getter(mtd) or AccessorMap.is_candidate_setter(mtd)

  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(AccessorMap.get_candidate_mtds, cls.subs))
    return filter(AccessorMap.is_candidate_mtd, mtds)

  # common params for getter methods (and part of setter methods)
  @staticmethod
  def getter_params():
    return [ (C.J.i, u"map_id"), (C.J.i, u"mtd_id"), (C.J.OBJ, u"callee") ]

  # TODO: value type is currently fixed to C.J.OBJ
  # code for getting a map
  @staticmethod
  def __getter(aux, ty):
    shorty = util.to_shorty_sk(ty)
    params = AccessorMap.getter_params() + [ (ty, u"key") ]
    getr = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=shorty+u"get")
    rtn = u"""
      Map<{0}, {1}> map = callee._prvt_{2}map[map_id];
      // intentionally not checking/calling contains to raise a semantic error
      return map.get(key);
    """.format(ty, C.J.OBJ, shorty)
    getr.body = to_statements(getr, rtn)
    aux.add_mtds([getr])
    setattr(aux, shorty + "gttr", getr)

  @staticmethod
  def getter(aux):
    AccessorMap.__getter(aux, C.J.OBJ)

  @staticmethod
  def igetter(aux):
    AccessorMap.__getter(aux, C.J.i)

  # TODO: value type is currently fixed to C.J.OBJ
  # code for setting a map
  @staticmethod
  def __setter(aux, ty):
    shorty = util.to_shorty_sk(ty)
    params = AccessorMap.getter_params() + [ (ty, u"key"), (C.J.OBJ, u"val") ]
    setr = Method(clazz=aux, mods=C.PBST, params=params, name=shorty+u"set")
    assign = u"""
      Map<{0}, {1}> map = callee._prvt_{2}map[map_id];
      map.put(key, val);
    """.format(ty, C.J.OBJ, shorty)
    setr.body = to_statements(setr, assign)
    aux.add_mtds([setr])
    setattr(aux, shorty + "sttr", setr)

  @staticmethod
  def setter(aux):
    AccessorMap.__setter(aux, C.J.OBJ)

  @staticmethod
  def isetter(aux):
    AccessorMap.__setter(aux, C.J.i)

  # getter will be invoked here
  @staticmethod
  def __getter_in_one(aux, conf, ty):
    shorty = util.to_shorty_sk(ty)
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (ty, u"key")]
    one = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=shorty+u"getterInOne")
    def getter_switch_whole(cl):
      def getter_switch(role):
        aname = aux.name
        v = getattr(aux, '_'.join([C.ACC.GET, cl, role]))
        f = getattr(aux, shorty + "gttr").name
        argpairs = [(C.J.i, getattr(aux, '_'.join([C.ACC.GS, cl, role])))] + params
        args = u", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) return {aname}.{f}({args});".format(**locals())
      roles = map(str, range(conf[cl][1]))
      return u"\nelse ".join(map(getter_switch, roles))
    one.body = to_statements(one, u"\nelse ".join(map(getter_switch_whole, filter(lambda x: conf[x][1] > 0, conf.iterkeys()))))
    aux.add_mtds([one])

  @staticmethod
  def getter_in_one(aux, conf):
    AccessorMap.__getter_in_one(aux, conf, C.J.OBJ)

  @staticmethod
  def igetter_in_one(aux, conf):
    AccessorMap.__getter_in_one(aux, conf, C.J.i)

  # setter will be invoked here
  @staticmethod
  def __setter_in_one(aux, conf, ty):
    shorty = util.to_shorty_sk(ty)
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (ty, u"key"), (C.J.OBJ, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=shorty+u"setterInOne")
    def setter_switch_whole(cl):
      def setter_switch(role):
        aname = aux.name
        v = getattr(aux, '_'.join([C.ACC.SET, cl, role]))
        f = getattr(aux, shorty + "sttr").name
        argpairs = [(C.J.i, getattr(aux, '_'.join([C.ACC.GS, cl, role])))]+params
        args = u", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      roles = map(str, range(conf[cl][2]))
      return u"\nelse ".join(map(setter_switch, roles))
    one.body = to_statements(one, u"\nelse ".join(map(setter_switch_whole, filter(lambda x: conf[x][2] > 0, conf.iterkeys()))))
    aux.add_mtds([one])

  @staticmethod
  def setter_in_one(aux, conf):
    AccessorMap.__setter_in_one(aux, conf, C.J.OBJ)

  @staticmethod
  def isetter_in_one(aux, conf):
    AccessorMap.__setter_in_one(aux, conf, C.J.i)

  @staticmethod
  def add_fld(cls, ty, nm):
    logging.debug("adding field {}.{} of type {}".format(cls.name, nm, ty))
    fld = Field(clazz=cls, typ=ty, name=nm)
    cls.add_flds([fld])
    cls.init_fld(fld)
    return fld

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
    checkers.extend(reduce(lambda x,y: x+y, map(getter_sig, conf.iterkeys()), []))
    checkers.extend(reduce(lambda x,y: x+y, map(setter_sig, conf.iterkeys()), []))
    checkers.extend(reduce(lambda x,y: x+y, map(gs_match, conf.iterkeys()), []))

    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    # getter pattern
    AccessorMap.getter(aux)
    AccessorMap.igetter(aux)

    AccessorMap.getter_in_one(aux, conf)
    AccessorMap.igetter_in_one(aux, conf)

    # setter pattern
    AccessorMap.setter(aux)
    AccessorMap.isetter(aux)

    AccessorMap.setter_in_one(aux, conf)
    AccessorMap.isetter_in_one(aux, conf)

    add_artifacts([aux.name])
    return aux


  @v.when(Template)
  def visit(self, node):
    self.find_clss_involved(node)
    aux = self.gen_aux_cls(self._acc_conf, node)
    node.add_classes([aux])

  @v.when(Clazz)
  def visit(self, node):
    if node.name == C.J.OBJ:
      AccessorMap.add_fld(node, u"Map<{},{}>[]".format(C.J.OBJ, C.J.OBJ), u"_prvt_map")
      AccessorMap.add_fld(node, u"Map<{},{}>[]".format(C.J.i, C.J.OBJ), u"_prvt_imap")

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    if node.annos: return
    if node.clazz.pkg in ["java.lang"]: return
    if node.clazz.client: return
    cname = node.clazz.name
    if cname in self._acc_default: return

    # getter candidate
    if AccessorMap.is_candidate_getter(node) and not node.has_return:
      shorty = util.to_shorty_sk(node.param_typs[0])
      mname = shorty + u"getterInOne"
      callee = C.J.N if node.is_static else C.J.THIS
      args = u", ".join([unicode(node.id), callee, node.params[0][1]])
      call = u"return {}({});".format(u".".join([self.aux_name, mname]), args)
      node.body += to_statements(node, call)
      logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))

    # setter candidate
    if AccessorMap.is_candidate_setter(node):
      shorty = util.to_shorty_sk(node.param_typs[0])
      mname = shorty + u"setterInOne"
      callee = C.J.N if node.is_static else C.J.THIS
      args = u", ".join([unicode(node.id), callee, node.params[0][1], node.params[1][1]])
      call = u"{}({});".format(u".".join([self.aux_name, mname]), args)
      node.body += to_statements(node, call)
      logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

