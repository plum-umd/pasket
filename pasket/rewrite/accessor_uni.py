import operator as op
from itertools import product, combinations
from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from .. import sample
from ..meta import class_lookup
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

    #self._max_param = max(map(lambda (c, g, s, i): c, acc_conf.values()))

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
  def is_candidate_cls(conf, c, cls):
    # skip java.lang.*
    if cls.pkg in ["java.lang"]: return False
    candidate_cls = [cls] 
    if cls.sup and class_lookup(cls.sup).is_class and (not class_lookup(cls.sup).pkg in ["java.lang"]):
     candidate_cls = [cls, class_lookup(cls.sup)]
    mtds = util.flatten(map(lambda cc: cc.mtds, candidate_cls))
    getter_mtds = filter(AccessorUni.is_candidate_getter, mtds)
    setter_mtds = filter(AccessorUni.is_candidate_setter, mtds)
    #cons_mtds = filter(lambda x: x.is_init, mtds)
    cons_mtds = AccessorUni.get_candidate_inits(conf, c, cls)
    return cls.is_class and len(getter_mtds)>=conf[c][1] and len(setter_mtds)>=conf[c][2] and any(set(cons_mtds) & set(mtds))

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

  @staticmethod
  def is_container(cls):
    name = cls.name
    return name == u"ArrayDeque" or name == u"LinkedList" or name == u"Stack" or name == u"TreeMap" or name == u"ArrayDequeue"

  # retrieve constructors
  @staticmethod
  def get_candidate_inits(conf, c, cls):
    if AccessorUni.is_container(cls) or cls.name == C.J.I or cls.name == C.J.STR or cls.name == C.J.v or cls.name == C.J.i or cls.name == C.J.z or cls.name == C.J.OBJ:
      return []
    else:
      return filter(lambda x: x.is_init and (conf[c][0] < 0 or len(x.params) + conf[c][3] == conf[c][0]), cls.mtds)

  # retrieve constructors
  @staticmethod
  def get_candidate_implicits(clss, cls):
    base_clss = map(lambda m: class_lookup(m.typ), filter(lambda m: not m.is_init and len(m.params) == 0 and m.typ != C.J.v and m.typ != C.J.i and m.typ != C.J.z, cls.mtds))
    candidate_clss = filter(lambda c: util.exists(lambda b: c <= b, base_clss), clss)
    real_clss = filter(lambda c: not AccessorUni.is_container(c) and c.name != C.J.I and c.name != C.J.STR and c.name != C.J.v and c.name != C.J.i and c.name != C.J.z and c.name != C.J.OBJ, candidate_clss)
    return filter(lambda c: util.exists(lambda m: m.name == c.name and len(m.params) == 0, c.mtds), real_clss)

  @staticmethod
  def get_candidate_imp(tmpl):
    return filter(lambda x: x.is_init and not x.is_abstract and C.mod.PB in x.mods and len(x.params) == 0 and not AccessorUni.is_container(x) and x.name != C.J.I and x.name != C.J.STR and x.name != C.J.v and x.name != C.J.i and x.name != C.J.z and x.name != C.J.OBJ, reduce(lambda x,y: x+y, map(lambda c: c.mtds, tmpl.classes)))

  # add a global counter
  @staticmethod
  def add_global_counter(aux, fname):
    z = to_expression(u"0")
    d = Field(clazz=aux, mods=C.PRST, typ=C.J.i, name=fname, init=z)
    aux.add_flds([d])
    return d

  # restrict call stack for the given method via a global counter
  @staticmethod
  def limit_depth(aux, mtd, depth, rval=u''):
    fname = mtd.name + "_depth"
    AccessorUni.add_global_counter(aux, fname)
    prologue = to_statements(mtd, u"""
      if ({fname} > {depth}) return {rval};
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

  # common params for implict mapping methods
  @staticmethod
  def mapping_params():
    return [ (C.J.i, u"cls_id"), (C.J.i, u"fld_id") ]

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

  # methods that simulates reflection
  @staticmethod
  def reflect_per_cls(aux, clss, cls):
    params = [(C.J.i, u"cons_id")]
    reflect = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=u"reflect_"+cls.name)
    cons = AccessorUni.get_candidate_implicits(clss, cls)
    logging.debug("{}.{} {}".format(aux.name, reflect.name, cons))
    def invoke(cons):
      call = "return new {}();".format(cons.name)
      return u"if (cons_id == {cons.id}) {{ {call} }}".format(**locals())
    invocations = filter(None, map(invoke, cons))
    tests = u"\nelse ".join(invocations)
    reflect.body = to_statements(reflect, tests)
    AccessorUni.limit_depth(aux, reflect, 2, u"null")
    aux.add_mtds([reflect])
    setattr(aux, "reflect_"+cls.name, reflect)

  # a method that simulates reflection
  @staticmethod
  def reflect(aux, clss):
    map(partial(AccessorUni.reflect_per_cls, aux, clss), filter(lambda c: c.name != C.J.OBJ and c.name != C.J.i and c.name != C.J.z and not AccessorUni.is_container(c), clss))

  #@staticmethod
  #def reflect(aux, clss):
  #  params = [(C.J.i, u"cons_id")]
  #  reflect = Method(clazz=aux, mods=C.PBST, typ=C.J.OBJ, params=params, name=u"reflect")
  #  def switch( cls ):
  #    cons = AccessorUni.get_candidate_implicits(clss, cls)
  #    logging.debug("{}.{} {}".format(aux.name, reflect.name, cons))
  #    def invoke(cons):
  #      call = "return new {}();".format(cons.name)
  #      return u"if (cons_id == {cons.id}) {{ {call} }}".format(**locals())
  #    invocations = filter(None, map(invoke, cons))
  #    #return "\nelse ".join(invocations)
  #    return invocations
  #  tests = set(sum(map(switch, filter(lambda c: c.name != C.J.OBJ and c.name != C.J.i and c.name != C.J.z and not AccessorUni.is_container(c), clss)), []))
  #  reflect.body = to_statements(reflect, u"\nelse ".join(tests))
  #  AccessorUni.limit_depth(aux, reflect, 2, u"null")
  #  aux.add_mtds([reflect])
  #  setattr(aux, "reflect", reflect)

  @staticmethod
  def implicit_cls_mapping(aux, conf, cls, fld_c, c_cnt):
    params = [ (C.J.i, u"fld_id") ]
    one = Method(clazz=aux, mods=C.PBST, typ=C.J.i, params=params, name=u"mapToID_"+cls)
    def implicit_map_switch(fld_id):
      v = getattr(aux, '_'.join([C.ACC.ACC, cls]))
      f = getattr(aux, '_'.join([C.ACC.IMP, cls, str(fld_id)]))
      return u"if (fld_id == {fld_id}) return {f};".format(**locals())
    one.body = to_statements(one, u"\nelse ".join(map(implicit_map_switch, range(conf[cls][0]))))
    AccessorUni.limit_number(one, fld_c, c_cnt, u"-1")
    aux.add_mtds([one])

  @staticmethod
  def implicit_mapping(aux, conf, fld_c, c_cnt):
    cls = conf.keys()
    map(lambda i: AccessorUni.implicit_cls_mapping(aux, conf, cls[i], fld_c, c_cnt), range(len(conf)))

  @staticmethod
  def implicit_in_one_per_cls(aux, conf, fld_c, c_cnt, tmpl, cls):
    params = AccessorUni.mapping_params() + [(C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"implicitInitInOne_"+cls.name)
    def implicit_switch_whole(cl_id):
      clid = cl_id
      cl = conf.keys()[cl_id]
      aname = aux.name
      f = getattr(aux, "sttr").name
      reflect = getattr(aux, "reflect_"+cls.name).name
      i = u"mapToID_{cl}(fld_id)".format(**locals())
      args = ", ".join(map(lambda (ty, nm): nm, params[1:2] + params[:1]) + [u"callee"] + [u"{reflect}(cons_id)".format(**locals())])
      u = getattr(aux, '_'.join([C.ACC.ACC, cl]))
      #v = u"mapToID({clid}, fld_id)".format(**locals())
      num_fld = unicode(conf[cl][0])
      call = "int cons_id = mapToID_{cl}(fld_id);\n{aname}.{f}({args});".format(**locals())
      return u"if ({u} == cls_id && fld_id < {num_fld}) {{ {call} }}".format(**locals())
    cand_ids = filter(lambda n: AccessorUni.is_candidate_cls(conf, conf.keys()[n], cls) and conf[conf.keys()[n]][0]>0 and conf[conf.keys()[n]][3], range(len(conf.keys())))
    if any(cand_ids):
      one.body = to_statements(one, "\nelse ".join(map(implicit_switch_whole, cand_ids)))
      AccessorUni.limit_number(one, fld_c, c_cnt)
      aux.add_mtds([one])

  @staticmethod
  def implicit_in_one(aux, conf, fld_c, c_cnt, tmpl):
    params = AccessorUni.mapping_params() + [(C.J.OBJ, u"callee")]
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"implicitInitInOne")
    def implicit_switch_whole(cl_id):
      clid = cl_id
      cl = conf.keys()[cl_id]
      aname = aux.name
      f = getattr(aux, "sttr").name
      #reflect = aux.reflect.name
      reflect = "reflect"
      i = u"mapToID_{cl}(fld_id)".format(**locals())
      args = ", ".join(map(lambda (ty, nm): nm, params[1:2] + params[:1]) + [u"callee"] + [u"{reflect}(cons_id)".format(**locals())])
      u = getattr(aux, '_'.join([C.ACC.ACC, cl]))
      #v = u"mapToID({clid}, fld_id)".format(**locals())
      call = "int cons_id = mapToID_{cl}(fld_id);\n{aname}.{f}({args});".format(**locals())
      return u"if ({u} == cls_id && ??) {{ {call} }}".format(**locals())
    one.body = to_statements(one, "\nelse ".join(map(implicit_switch_whole, filter(lambda n: conf[conf.keys()[n]][0]>0 and conf[conf.keys()[n]][3], range(len(conf.keys()))))))
    AccessorUni.limit_number(one, fld_c, c_cnt)
    aux.add_mtds([one])

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

    def get_f_roles(name, c):
      return map(lambda n: '_'.join([name, c, str(n)]), range(conf[c][0]))
    def get_g_roles(name, c):
      return map(lambda n: '_'.join([name, c, str(n)]), range(conf[c][1]))
    def get_s_roles(name, c):
      return map(lambda n: '_'.join([name, c, str(n)]), range(conf[c][2]))

    rv_gtts = util.flatten(map(partial(get_g_roles, C.ACC.GET), conf.iterkeys()))
    rv_stts = util.flatten(map(partial(get_s_roles, C.ACC.SET), conf.iterkeys()))
    rv_imp = util.flatten(map(partial(get_f_roles, C.ACC.IMP), conf.iterkeys()))
    gs_vars = util.flatten(map(partial(get_g_roles, C.ACC.GS), conf.iterkeys()))

    # set role variables
    def set_role(role):
      setattr(aux, role, '_'.join([role, aux.name]))
    map(set_role, rv_cons)
    #map(set_role, constructor_args)
    map(set_role, rv_accs)
    map(set_role, rv_gtts)
    map(set_role, rv_stts)
    map(set_role, rv_imp)
    map(set_role, gs_vars)
    
    # add fields that stand for non-deterministic role choices
    def aux_fld(init, ty, nm):
      if hasattr(aux, nm): nm = getattr(aux, nm)
      return Field(clazz=aux, mods=[C.mod.ST], typ=ty, name=nm, init=init)

    #hole = to_expression(C.T.HOLE)
    #aux_int = partial(aux_fld, hole, C.J.i)

    c_to_e = lambda c: to_expression(unicode(c))
    gen_range = lambda ids: gen_E_gen(map(c_to_e, util.rm_dup(ids)))
    get_id = op.attrgetter("id")
    get_name = op.attrgetter("name")

    #aux.add_flds(map(aux_int, gs_vars))
    for c in conf:
      hole = gen_range(range(conf[c][0]))
      aux_int = partial(aux_fld, hole, C.J.i)
      aux.add_flds(map(aux_int, get_g_roles(C.ACC.GS, c)))


    # range check for getter/setter
    mtds = util.flatten(map(AccessorUni.get_candidate_mtds, self._clss))

    # auxiliary functions
    def aux_getter_range(conf, c, nm, mtds, num_args, is_void):
      cand_mtds = filter(lambda m: AccessorUni.is_candidate_getter(m) and len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds)
      ids = map(get_id, cand_mtds)
      #ids = map(get_id, filter(lambda m: AccessorUni.is_candidate_cls(conf, c, m.clazz) and len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds))
      init = gen_range(ids)
      role = getattr(aux, '_'.join(map(str, [C.ACC.GET, c, nm])))
      aux.add_flds([aux_fld(init, C.J.i, role)])

    # auxiliary functions
    def aux_setter_range(conf, c, nm, mtds, num_args, is_void):
      cand_mtds = filter(lambda m: AccessorUni.is_candidate_setter(m) and len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds)
      ids = map(get_id, cand_mtds)
      #ids = map(get_id, filter(lambda m: AccessorUni.is_candidate_cls(conf, c, m.clazz) and len(m.params) == num_args and (m.typ == C.J.v) == is_void, mtds))
      init = gen_range(ids)
      role = getattr(aux, '_'.join(map(str, [C.ACC.SET, c, nm])))
      aux.add_flds([aux_fld(init, C.J.i, role)])

    def mtd_range(c):
      map(lambda m: [aux_getter_range(conf, c, m, mtds, 0, False)], range(conf[c][1]))
      map(lambda m: [aux_setter_range(conf, c, m, mtds, 1, True)], range(conf[c][2]))

    def imp_range(rl):
      cand_names = map(get_name, AccessorUni.get_candidate_imp(tmpl))
      ids = map(get_id, filter(lambda c: c.name in cand_names, self._clss))
      init = gen_range(ids)
      role = getattr(aux, rl)
      aux.add_flds([aux_fld(init, C.J.i, role)])

    def gs_positive(role, num):
      rv = getattr(aux, '_'.join([C.ACC.GS, role, str(num)]))
      argnum = conf[role][0]
      if argnum < 0:
        checkers.append("assert {rv} >= 0;".format(**locals()))
      else:
        checkers.append("assert {rv} >= 0 && {rv} < {argnum};".format(**locals()))

    def owner_range(rl, c, ids):
      return map(lambda i: "assert subcls("+getattr(aux, '_'.join([C.ACC.ACC, c]))+", belongsTo("+getattr(aux, '_'.join([rl, c, str(i)]))+"));", ids)

    def bundle_getter_setter(c, gids, sids):
      return map(lambda (g, s): "assert belongsTo("+getattr(aux, '_'.join([C.ACC.GET, c, str(g)])) + ") == belongsTo(" + getattr(aux, '_'.join([C.ACC.SET, c, str(s)])) + ");", product(gids, sids))

    def getter_sig(c):
      return map(lambda i: "assert (argNum(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)])) + ")) == 0;", range(conf[c][1]))
    def setter_sig(c):
      return map(lambda i: "assert (argNum(" + getattr(aux, '_'.join([C.ACC.SET, c, str(i)])) + ")) == 1;", range(conf[c][2]))
    def gs_match(c):
      return map(lambda i: "assert subcls(argType(" + getattr(aux, '_'.join([C.ACC.SET, c, str(i)]))+", 0), retType(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)])) + "));", range(conf[c][2]))
    def gs_type_match(c):
      if conf[c][0] < 0: return []
      else:
	cons = getattr(aux, '_'.join([C.ACC.CONS, c]))
	fldnum = lambda j: getattr(aux, '_'.join([C.ACC.GS, c, str(j)]))
        return map(lambda i: "if (argNum(" + cons + ") > " + fldnum(i) + ") assert argType(" + cons + ", " + fldnum(i) + ") == retType(" + getattr(aux, '_'.join([C.ACC.GET, c, str(i)]))+");", range(conf[c][1]))



    # range check for constructors
    #inits = util.flatten(map(lambda c: filter(lambda x: x.is_init and len(x.params) <= conf[], c.mtds), self._clss))
    #inits = util.flatten(map(AccessorUni.get_candidate_inits, self._clss))

    map(mtd_range, conf.iterkeys())

    map(imp_range, rv_imp)

    # disjoint accessors
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"disjointAccessor")
    checkers = []
    for r_i, r_j in combinations(rv_accs, 2):
      checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")
    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    # disjoint constructors
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"disjointConstructor")
    checkers = []
    for r_i, r_j in combinations(rv_cons, 2):
      checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")
    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    # Don't mess up multiple instances
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"disjointInstance")
    checkers = []
    for r_i in conf.keys():
      for r_j in conf.keys():
        if r_i != r_j:
          for n in range(conf[r_j][1]):
            checkers.append("assert " + getattr(aux, '_'.join([C.ACC.ACC, r_i])) + " != belongsTo(" + getattr(aux, '_'.join([C.ACC.GET, r_j, str(n)])) + ");")
    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    # disjoint getters
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"disjointGetter")
    checkers = []
    for r_i, r_j in combinations(rv_gtts, 2):
      checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")
    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    # disjoint setters
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"disjointSetter")
    checkers = []
    for r_i, r_j in combinations(rv_stts, 2):
      checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")
    rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
    aux.add_mtds([rg_chk])

    # add fields
    for c in conf:
      cand_cls = filter(lambda cls: AccessorUni.is_candidate_cls(conf, c, cls), self._clss)
      cls_ids = map(get_id, cand_cls)
      cls_init = gen_range(cls_ids)
      aux_int_cls = partial(aux_fld, cls_init, C.J.i)
      aux.add_flds([aux_fld(cls_init, C.J.i, u'_'.join([C.ACC.ACC, c]))])

      inits = util.flatten(map(lambda cls: AccessorUni.get_candidate_inits(conf, c, cls), cand_cls))
      cons_ids = map(get_id, inits)
      cons_init = gen_range(cons_ids)
      aux.add_flds([aux_fld(cons_init, C.J.i, u'_'.join([C.ACC.CONS, c]))])

    for c in conf:
      if conf[c][1] > 1:
        # disjoint gs fields in the same configuration
        rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"disjointGSFor"+c)
        checkers = []
        c_gs_vars = map(lambda n: '_'.join([C.ACC.GS, c, str(n)]), range(conf[c][1]))
        for r_i, r_j in combinations(c_gs_vars, 2):
          checkers.append("assert " + getattr(aux, r_i) + " != " + getattr(aux, r_j) + ";")
        rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
        aux.add_mtds([rg_chk])

      if conf[c][1] > 0:
        # match getter/setter
        rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"matchGSFor"+c)
        checkers = []
        checkers.extend(gs_match(c))
        checkers.extend(gs_type_match(c))
        rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
        aux.add_mtds([rg_chk])

    # check range
    for c in conf:
      rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRangeFor"+c)
      checkers = []
      # range check for gs: as an index, shouldn't be negative
      #map(partial(gs_positive, c), range(conf[c][1]))
      if conf[c][0] >= 0:
        #checkers.append("assert (argNum(" + getattr(aux, '_'.join([C.ACC.CONS, c])) + ")) <= " + str(conf[c][0]) + ";")
        checkers.append("assert (belongsTo(" + getattr(aux, '_'.join([C.ACC.CONS, c])) + ")) == " + getattr(aux, '_'.join([C.ACC.ACC, c])) + ";")
      # other semantics checks
      # such as ownership, bundle getter/setter, and signature types
      checkers.extend(owner_range(C.ACC.GET, c, range(conf[c][1])))
      checkers.extend(owner_range(C.ACC.SET, c, range(conf[c][2])))

      checkers.extend(bundle_getter_setter(c, range(conf[c][1]), range(conf[c][2])))
      #checkers.extend(getter_sig(c))
      #checkers.extend(setter_sig(c))

      rg_chk.body += to_statements(rg_chk, u'\n'.join(checkers))
      aux.add_mtds([rg_chk])
    

    # assumption: # of objects and events could be instantiated
    obj_cnt = sample.max_objs(self._smpls)
    evt_cnt = sample.max_evts(self._smpls)
    arg_cnt = sum(map(lambda (c, g, s, i): c, self._acc_conf.values()))
    c_cnt = (obj_cnt + evt_cnt + 1) * arg_cnt

    # assumption: each getter could be invoked per event
    g_cnt = sum(map(lambda (c, g, s, i): g, self._acc_conf.values()))
    g_cnt = g_cnt * max(1, evt_cnt)

    # assumption: setter could be invoked once, excluding constructor
    s_cnt = sum(map(lambda (c, g, s, i): s, self._acc_conf.values()))
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
    
    # implicit constructor
    
    AccessorUni.reflect(aux, tmpl.classes)
    AccessorUni.implicit_mapping(aux, conf, fld_c, c_cnt)
    #AccessorUni.implicit_in_one(aux, conf, fld_c, c_cnt, tmpl)
    map(lambda cls: AccessorUni.implicit_in_one_per_cls(aux, conf, fld_c, c_cnt, tmpl, cls), filter(lambda c: c.name != C.J.OBJ and not AccessorUni.is_container(c), tmpl.classes))

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
    if node.is_init and node.name != C.J.OBJ and node.name != u"EventType" and not AccessorUni.is_container(node.clazz):
      for i in xrange(len(node.params)):
        if str(node.params[i][1]) in used_args:
          continue
        shorty = util.to_shorty_sk(node.params[i][0])
        mname = shorty + u"constructorInOne"
        fid = unicode(i)
        args = ", ".join([fid, unicode(node.id), C.J.THIS, unicode(node.params[i][1])])
        node.body += to_statements(node, u"{}.{}({});".format(self.aux_name, mname, args))
        logging.debug("{}.{} => {}.{}".format(cname, node.name, self.aux_name, mname))
      cls = node.clazz
      conf = self._acc_conf
      cand_ids = filter(lambda n: AccessorUni.is_candidate_cls(conf, conf.keys()[n], cls) and conf[conf.keys()[n]][0]>0 and conf[conf.keys()[n]][3], range(len(conf.keys())))
      if not cls.is_inner and any(cand_ids):
        max_param = max(map(lambda n: conf[conf.keys()[n]][0], cand_ids))
        for j in xrange(max_param - len(node.params)):
	  mname = u"implicitInitInOne_" + cls.name
	  #mname = u"implicitInitInOne"
	  fid = unicode(len(node.params) + j)	
          args = ", ".join([unicode(node.clazz.id), fid, C.J.THIS])
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

