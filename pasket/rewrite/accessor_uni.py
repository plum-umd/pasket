import operator as op
from itertools import product, combinations
from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from .. import sample
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression, to_expression, gen_E_gen

class AccessorUni(object):

  def __init__(self, smpls, acc_default, acc_conf):
    self._smpls = smpls
    self._acc_default = acc_default
    self._acc_conf = acc_conf

    self._clss = []
    self._aux_name = C.ACC.AUX+"Uni"
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

  # find possible classes for Getter/Setter
  # assume all classes (except for interfaces) are candidates
  def find_clss_involved(self, tmpl):
    for cls in util.flatten_classes(tmpl.classes, "inners"):
      # ignore interface
      if cls.is_itf and not cls.subs:
        logging.debug("ignore interface {}".format(cls.name))
        continue
      self._clss.append(cls)

  @staticmethod
  def is_candidate_cls(cls):
    # skip java.lang.*
    if cls.pkg in ["java.lang"]: return False
    mtds = cls.mtds
    getter_mtds = filter(AccessorUni.is_candidate_getter, mtds)
    cons_mtds = AccessorUni.get_candidate_inits(cls)
    return cls.is_class and (any(getter_mtds) or any(cons_mtds))

  @staticmethod
  def is_candidate_getter(mtd):
    return not mtd.is_init and not mtd.is_abstract and \
        len(mtd.params) == 0 and mtd.typ != C.J.v

  @staticmethod
  def is_candidate_setter(mtd):
    return not mtd.is_init and not mtd.is_abstract and \
        len(mtd.params) == 1 and mtd.typ == C.J.v

  # assume methods that participate will be neither <init> nor static
  @staticmethod
  def is_candidate_mtd(mtd):
    return not mtd.is_init and not mtd.is_static

  # retrieve candidate methods (in general)
  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(op.attrgetter("mtds"), cls.subs))
    return filter(AccessorUni.is_candidate_mtd, mtds)

  # retrieve constructors
  @staticmethod
  def get_candidate_inits(cls):
    return filter(lambda x: x.is_init, cls.mtds)

  # add a global counter
  @staticmethod
  def add_global_counter(aux, fname):
    z = to_expression(u"0")
    d = Field(clazz=aux, mods=C.PRST, typ=C.J.i, name=fname, init=z)
    aux.add_flds([d])
    return d

  # restrict call stack for the given method via a global counter
  @staticmethod
  def limit_depth(aux, mtd, depth):
    fname = mtd.name + "_depth"
    AccessorUni.add_global_counter(aux, fname)
    prologue = to_statements(mtd, u"""
      if ({fname} > {depth}) return;
      {fname} = {fname} + 1;
    """.format(**locals()))
    epilogue = to_statements(mtd, u"""
      {fname} = {fname} - 1;
    """.format(**locals()))
    mtd.body = prologue + mtd.body + epilogue

  # restrict the number of the method invocations
  @staticmethod
  def limit_number(mtd, fld, cnt, rval=u''):
    fname = fld.name
    guard = to_statements(mtd, u"""
      if ({fname} > {cnt}) return {rval};
      {fname} = {fname} + 1;
    """.format(**locals()))
    mtd.body = guard + mtd.body
  
  # common params for getter methods (and part of setter methods)
  @staticmethod
  def getter_params():
    return [ (C.J.i, u"fld_id"), (C.J.i, u"mtd_id"), (C.J.OBJ, u"callee") ]

  # code for getting a field
  @staticmethod
  def __getter(aux, ty):
    shorty = util.to_shorty_sk(ty)
    params = AccessorUni.getter_params()
    getr = Method(clazz=aux, mods=C.PBST, typ=ty, params=params, name=shorty+u"get")
    rtn = u"return callee._prvt_{}fld[fld_id];".format(shorty)
    getr.body = to_statements(getr, rtn)
    aux.add_mtds([getr])
    setattr(aux, shorty + "gttr", getr)

  @staticmethod
  def getter(aux):
    AccessorUni.__getter(aux, C.J.OBJ)
  
  @staticmethod
  def igetter(aux):
    AccessorUni.__getter(aux, C.J.i)
  
  @staticmethod
  def zgetter(aux):
    AccessorUni.__getter(aux, C.J.z)
  
  # code for setting a field
  @staticmethod
  def __setter(aux, ty):
    shorty = util.to_shorty_sk(ty)
    params = AccessorUni.getter_params() + [(ty, u"val")]
    setr = Method(clazz=aux, mods=C.PBST, params=params, name=shorty+u"set")
    assign = u"callee._prvt_{}fld[fld_id] = val;".format(shorty)
    setr.body = to_statements(setr, assign)
    aux.add_mtds([setr])
    setattr(aux, shorty + "sttr", setr)

  @staticmethod
  def setter(aux):
    AccessorUni.__setter(aux, C.J.OBJ)
  
  @staticmethod
  def isetter(aux):
    AccessorUni.__setter(aux, C.J.i)
  
  @staticmethod
  def zsetter(aux):
    AccessorUni.__setter(aux, C.J.z)
  
  # getter will be invoked here
  @staticmethod
  def __getter_in_one(aux, conf, fld_g, g_cnt, ty, default):
    shorty = util.to_shorty_sk(ty)
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, typ=ty, params=params, name=shorty+u"getterInOne")
    def getter_switch_whole(cl):
      def getter_switch(role):
        aname = aux.name
        v = getattr(aux, '_'.join([C.ACC.GET, cl, role]))
        f = getattr(aux, shorty + "gttr").name
        argpairs = [(C.J.i, getattr(aux, '_'.join([C.ACC.GS, cl, role])))] + params
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) return {aname}.{f}({args});".format(**locals())
      roles = map(str, range(conf[cl][1]))
      return "\nelse ".join(map(getter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(getter_switch_whole, filter(lambda x: conf[x][1] > 0, conf.iterkeys()))))
    AccessorUni.limit_number(one, fld_g, g_cnt, default)
    aux.add_mtds([one])

  @staticmethod
  def getter_in_one(aux, conf, fld_g, g_cnt):
    AccessorUni.__getter_in_one(aux, conf, fld_g, g_cnt, C.J.OBJ, C.J.N)
  
  @staticmethod
  def igetter_in_one(aux, conf, fld_g, g_cnt):
    AccessorUni.__getter_in_one(aux, conf, fld_g, g_cnt, C.J.i, u"-1")
  
  @staticmethod
  def zgetter_in_one(aux, conf, fld_g, g_cnt):
    AccessorUni.__getter_in_one(aux, conf, fld_g, g_cnt, C.J.z, C.J.FALSE)
  
  # setter will be invoked here
  @staticmethod
  def __setter_in_one(aux, conf, fld_s, s_cnt, ty):
    shorty = util.to_shorty_sk(ty)
    params = [(C.J.i, u"mtd_id"), (C.J.OBJ, u"callee"), (ty, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=shorty+u"setterInOne")
    def setter_switch_whole(cl):
      def setter_switch(role):
        aname = aux.name
        v = getattr(aux, '_'.join([C.ACC.SET, cl, role]))
        f = getattr(aux, shorty + "sttr").name
        argpairs = [(C.J.i, getattr(aux, '_'.join([C.ACC.GS, cl, role])))] + params
        args = ", ".join(map(lambda (ty, nm): nm, argpairs))
        return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
      roles = map(str, range(conf[cl][2]))
      return "\nelse ".join(map(setter_switch, roles))
    one.body = to_statements(one, "\nelse ".join(map(setter_switch_whole, filter(lambda x: conf[x][2] > 0, conf.iterkeys()))))
    AccessorUni.limit_number(one, fld_s, s_cnt)
    aux.add_mtds([one])

  @staticmethod
  def setter_in_one(aux, conf, fld_s, s_cnt):
    AccessorUni.__setter_in_one(aux, conf, fld_s, s_cnt, C.J.OBJ)
  
  @staticmethod
  def isetter_in_one(aux, conf, fld_s, s_cnt):
    AccessorUni.__setter_in_one(aux, conf, fld_s, s_cnt, C.J.i)
  
  @staticmethod
  def zsetter_in_one(aux, conf, fld_s, s_cnt):
    AccessorUni.__setter_in_one(aux, conf, fld_s, s_cnt, C.J.z)
  
  # initializer will be invoked here
  @staticmethod
  def __constructor_in_one(aux, conf, fld_c, c_cnt, ty):
    shorty = util.to_shorty_sk(ty)
    params = AccessorUni.getter_params() + [(ty, u"val")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=shorty+u"constructorInOne")
    def constructor_switch_whole(cl):
      aname = aux.name
      v = getattr(aux, '_'.join([C.ACC.CONS, cl]))
      f = getattr(aux, shorty + "sttr").name
      argpairs = params
      args = ", ".join(map(lambda (ty, nm): nm, argpairs))
      return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
    one.body = to_statements(one, "\nelse ".join(map(constructor_switch_whole, filter(lambda n: conf[n][0]>=0, conf.iterkeys()))))
    AccessorUni.limit_number(one, fld_c, c_cnt)
    aux.add_mtds([one])

  @staticmethod
  def constructor_in_one(aux, conf, fld_c, c_cnt):
    AccessorUni.__constructor_in_one(aux, conf, fld_c, c_cnt, C.J.OBJ)
  
  @staticmethod
  def iconstructor_in_one(aux, conf, fld_c, c_cnt):
    AccessorUni.__constructor_in_one(aux, conf, fld_c, c_cnt, C.J.i)

  @staticmethod
  def zconstructor_in_one(aux, conf, fld_c, c_cnt):
    AccessorUni.__constructor_in_one(aux, conf, fld_c, c_cnt, C.J.z)

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
    tmpl.acc_auxs.append(self.aux_name)
    aux = Clazz(name=self.aux_name, mods=[C.mod.PB], subs=self._clss)
    self.aux = aux

    rv_cons = []
    for c in conf:
      if conf[c][0] >= 0:
        rv_cons.append('_'.join([C.ACC.CONS, c]))

    #constructor_args = []
    #for c in conf:
    #  new_args = map(lambda n: '_'.join([C.ACC.CONS, c, str(n)]), range(conf[c][0]))
    #  constructor_args.extend(new_args)
    
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
    map(set_role, rv_cons)
    #map(set_role, constructor_args)
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
    gen_range = lambda ids: gen_E_gen(map(c_to_e, util.rm_dup(ids)))
    get_id = op.attrgetter("id")

    # range check for accessors
    cls_ids = map(get_id, filter(AccessorUni.is_candidate_cls, self._clss))
    cls_init = gen_range(cls_ids)
    aux_int_cls = partial(aux_fld, cls_init, C.J.i)
    aux.add_flds(map(aux_int_cls, rv_accs))

    # range check for getter/setter
    mtds = util.flatten(map(AccessorUni.get_candidate_mtds, self._clss))

    def aux_range(rl, c, nm, mtds, num_args, is_void):
      ids = map(get_id, filter(lambda m: len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds))
      init = gen_range(ids)
      role = getattr(aux, '_'.join(map(str, [rl, c, nm])))
      aux.add_flds([aux_fld(init, C.J.i, role)])

    def mtd_range(c):
      map(lambda m: [aux_range(C.ACC.GET, c, m, mtds, 0, False)], range(conf[c][1]))
      map(lambda m: [aux_range(C.ACC.SET, c, m, mtds, 1, True)], range(conf[c][2]))
    map(mtd_range, conf.iterkeys())

    # disjoint getters
    for r_i, r_j in combinations(rv_gtts, 2):
      checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")

    # disjoint setters
    for r_i, r_j in combinations(rv_stts, 2):
      checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")

    # disjoint gs fields in the same configuration
    for c in conf:
      c_gs_vars = map(lambda n: '_'.join([C.ACC.GS, c, str(n)]), range(conf[c][1]))
      for r_i, r_j in combinations(c_gs_vars, 2):
        checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")
    
    # range check for gs: as an index, shouldn't be negative
    def gs_positive(role):
      rv = getattr(aux, role)
      checkers.append("assert {} >= 0;".format(rv))
    map(gs_positive, gs_vars)

    # range check for constructors
    inits = util.flatten(map(AccessorUni.get_candidate_inits, self._clss))
    cons_ids = map(get_id, inits)
    cons_init = gen_range(cons_ids)
    aux_int_cons = partial(aux_fld, cons_init, C.J.i)
    aux.add_flds(map(aux_int_cons, rv_cons))

    for c in conf.iterkeys():
      if conf[c][0] >= 0:
        checkers.append("assert (argNum(" + getattr(aux, '_'.join([C.ACC.CONS, c])) + ")) == " + str(conf[c][0]) + ";")
        checkers.append("assert (belongsTo(" + getattr(aux, '_'.join([C.ACC.CONS, c])) + ")) == " + getattr(aux, '_'.join([C.ACC.ACC, c])) + ";")

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
      return map(lambda i: "assert (argNum(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)])) + ")) == 0;", range(conf[c][1]))
    def setter_sig(c):
      return map(lambda i: "assert (argNum(" + getattr(aux, '_'.join([C.ACC.SET, c, str(i)])) + ")) == 1;", range(conf[c][2]))
    def gs_match(c):
      return map(lambda i: "assert subcls(argType(" + getattr(aux, '_'.join([C.ACC.SET, c, str(i)]))+", 0), retType(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)])) + "));", range(conf[c][2]))
    def gs_type_match(c):
      if conf[c][0] < 0: return []
      else:
        return map(lambda i: "assert argType(" + getattr(aux, '_'.join([C.ACC.CONS, c])) + ", " + getattr(aux, '_'.join([C.ACC.GS, c, str(i)]))+") == retType(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)]))+");", range(conf[c][1]))
    checkers.extend(reduce(lambda x,y: x+y, map(getter_sig, conf.iterkeys()), []))
    checkers.extend(reduce(lambda x,y: x+y, map(setter_sig, conf.iterkeys()), []))
    checkers.extend(reduce(lambda x,y: x+y, map(gs_match, conf.iterkeys()), []))
    checkers.extend(reduce(lambda x,y: x+y, map(gs_type_match, conf.iterkeys()), []))

    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])
    
    ## global counters

    # assumption: # of objects and events could be instantiated
    obj_cnt = sample.max_objs(self._smpls)
    evt_cnt = sample.max_evts(self._smpls)
    arg_cnt = sum(map(lambda (c, g, s): c, self._acc_conf.values()))
    c_cnt = (obj_cnt + evt_cnt + 1) * arg_cnt

    # assumption: each getter could be invoked per event
    g_cnt = sum(map(lambda (c, g, s): g, self._acc_conf.values()))
    g_cnt = g_cnt * max(1, evt_cnt)

    # assumption: setter could be invoked once, excluding constructor
    s_cnt = sum(map(lambda (c, g, s): s, self._acc_conf.values()))
    s_cnt = s_cnt * max(1, evt_cnt)
    s_cnt = s_cnt + c_cnt # as constructor can call setter

    # getter pattern

    AccessorUni.getter(aux)
    AccessorUni.igetter(aux)
    AccessorUni.zgetter(aux)

    fld_g = AccessorUni.add_global_counter(aux, u"getter_cnt")

    AccessorUni.getter_in_one(aux, conf, fld_g, g_cnt)
    AccessorUni.igetter_in_one(aux, conf, fld_g, g_cnt)
    AccessorUni.zgetter_in_one(aux, conf, fld_g, g_cnt)

    # setter pattern

    AccessorUni.setter(aux)
    AccessorUni.isetter(aux)
    AccessorUni.zsetter(aux)

    fld_s = AccessorUni.add_global_counter(aux, u"setter_cnt")

    AccessorUni.setter_in_one(aux, conf, fld_s, s_cnt)
    AccessorUni.isetter_in_one(aux, conf, fld_s, s_cnt)
    AccessorUni.zsetter_in_one(aux, conf, fld_s, s_cnt)

    # constructor pattern

    fld_c = AccessorUni.add_global_counter(aux, "constructor_cnt")

    AccessorUni.constructor_in_one(aux, conf, fld_c, c_cnt)
    AccessorUni.iconstructor_in_one(aux, conf, fld_c, c_cnt)
    AccessorUni.zconstructor_in_one(aux, conf, fld_c, c_cnt)

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
      AccessorUni.add_fld(node, self.aux.name+u"[]", u"_prvt_fld")
      AccessorUni.add_fld(node, C.J.i+u"[]", u"_prvt_ifld")
      AccessorUni.add_fld(node, C.J.z+u"[]", u"_prvt_zfld")

  @v.when(Field)
  def visit(self, node): pass

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
    cname = node.clazz.name
    if cname in self._acc_default: return
 
    # constructors
    used_args = []
    if node.body and node.body[0].kind == C.S.EXP and node.body[0].e.has_call: 
      used_args = map(str, node.body[0].e.a)
    if node.is_init:
      for i in xrange(len(node.params)):
        if str(node.params[i][1]) in used_args:
          continue
        shorty = util.to_shorty_sk(node.params[i][0])
        mname = shorty + u"constructorInOne"
        fid = unicode(i)
        args = ", ".join([fid, unicode(node.id), C.J.THIS, unicode(node.params[i][1])])
        node.body += to_statements(node, u"{}.{}({});".format(self.aux_name, mname, args))
        logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))
      return
    
    # getter candidate
    if AccessorUni.is_candidate_getter(node) and not node.has_return:
      shorty = util.to_shorty_sk(node.typ)
      mname = shorty + u"getterInOne"
      callee = C.J.N if node.is_static else C.J.THIS
      args = u", ".join([unicode(node.id), callee])
      call = u"return {}({});".format(u".".join([self.aux_name, mname]), args)
      node.body += to_statements(node, call)
      logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))

    # setter candidate
    if AccessorUni.is_candidate_setter(node):
      shorty = util.to_shorty_sk(node.param_typs[0])
      mname = shorty + u"setterInOne"
      callee = C.J.N if node.is_static else C.J.THIS
      args = u", ".join([unicode(node.id), callee, node.params[0][1]])
      call = u"{}({});".format(u".".join([self.aux_name, mname]), args)
      node.body += to_statements(node, call)
      logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))

  @v.when(Statement)
  def visit(self, node): return [node]

  @v.when(Expression)
  def visit(self, node): return node

