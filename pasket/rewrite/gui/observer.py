import copy as cp
import operator as op
from functools import partial
from itertools import permutations
import logging

import lib.const as C
import lib.visit as v

from ... import add_artifacts
from ... import util
from ... import sample
from ...encoder import add_ty_map
from ...meta import class_lookup
from ...meta.template import Template
from ...meta.clazz import Clazz, merge_flat
from ...meta.method import Method, sig_match, call_stt
from ...meta.field import Field
from ...meta.statement import Statement, to_statements
from ...meta.expression import Expression, to_expression, gen_E_gen

class Observer(object):

  @classmethod
  def find_obs(cls):
    return lambda anno: anno.by_name(C.A.OBS)

  # to build unique aux class names
  __cnt = 0

  @classmethod
  def new_aux(cls):
    cls.__cnt = cls.__cnt + 1
    return u"{}{}".format(C.OBS.AUX, cls.__cnt)

  def __init__(self, smpls):
    self._smpls = smpls
    self._tmpl = None
    self._eq = None
    self._cur_cls = None
    self._cur_mtd = None
    # classes that are involved in this pattern
    self._clss = {} # { E1: [C1, D1], E2: [C2, D1], ... }
    # event name to aux class name
    self._evts = {} # { E1: Aux1, E2: Aux2, ... }
    # class name to aux class names
    self._auxs = {} # { C1: [Aux1], D1: [Aux1, Aux2], C2: [Aux2], ... }
    # (subjectCall) methods to aux class name
    self._subj_mtds = {} # { M1: [Aux1], M2: [Aux1, Aux2], ... }

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  # find possible classes for @Subject and @Observer
  # so as to build self._clss and self._auxs
  # at this point, assume those are annotated with @ObserverPattern(E+)
  def find_clss_involved_w_anno_evt(self, tmpl):
    for cls in tmpl.classes:
      if not util.exists(Observer.find_obs(), cls.annos): continue

      # ignore interface without implementers
      if cls.is_itf and not cls.subs:
        logging.debug("ignore {} due to no implementers".format(cls.name))
        continue

      events = util.find(Observer.find_obs(), cls.annos).events
      for event in events:
        util.mk_or_append(self._clss, event, cls)

    for event in self._clss.keys():
      # if # of candidates is less than 2, ignore that event
      if len(self._clss[event]) < 2:
        logging.debug("ignore {} {}".format(event, self._clss[event]))
        del self._clss[event]
        del tmpl.events[event]
        continue

      aux_name = Observer.new_aux()
      tmpl.obs_auxs[aux_name] = self._clss[event]
      self._evts[event] = aux_name
      logging.debug("{}: {} {}".format(event, aux_name, self._clss[event]))
      for cls in self._clss[event]:
        util.mk_or_append(self._auxs, cls.name, aux_name)


  # find possible classes for @Subject and @Observer
  # so as to build self._clss and self._auxs
  # at this point, assume those are annotated with @ObserverPattern
  def find_clss_involved_w_anno(self, tmpl):
    #target_events = tmpl.events
    target_events = sample.evt_kinds(self._smpls)
    logging.debug("target events: {}".format(target_events))

    for cls in tmpl.classes:
      if not util.exists(Observer.find_obs(), cls.annos): continue
      # ignore interface without implementers
      if cls.is_itf and not cls.subs:
        logging.debug("ignore {} due to no implementers".format(cls.name))
        continue

      involved_clss = cls.param_typs
      for event in target_events:
        cls_e = class_lookup(event)
        for cls_i in map(class_lookup, involved_clss):
          if cls_i and cls_e <= cls_i:
            util.mk_or_append(self._clss, event, cls)

    for event in self._clss.keys():
      # if # of candidates is less than 2, ignore that event
      if len(self._clss[event]) < 2:
        logging.debug("ignore {} {}".format(event, self._clss[event]))
        del self._clss[event]
        del tmpl.events[event]
        continue
    
      aux_name = Observer.new_aux()
      tmpl.obs_auxs[aux_name] = self._clss[event]
      self._evts[event] = aux_name
      logging.debug("{}: {} {}".format(event, aux_name, self._clss[event]))
      for cls in self._clss[event]:
        util.mk_or_append(self._auxs, cls.name, aux_name)


  # find possible classes for @Subject and @Observer
  # so as to build self._clss and self._auxs
  # at this point, annotations are no longer used
  def find_clss_involved_wo_anno(self, tmpl):
    event = "AWTEvent"
    self._clss[event] = []

    for cls in tmpl.classes:
      if not util.exists(Observer.find_obs(), cls.annos): continue
      # ignore interface without implementers
      if cls.is_itf and not cls.subs:
        logging.debug("ignore {} due to no implementers".format(cls.name))
        continue

      util.mk_or_append(self._clss, event, cls)
    
    for e in tmpl.events.keys():
      if e != event:
        del tmpl.events[e]

    aux_name = Observer.new_aux()
    tmpl.obs_auxs[aux_name] = self._clss[event]
    self._evts[event] = aux_name
    logging.debug("{}: {} {}".format(event, aux_name, self._clss[event]))
    for cls in self._clss[event]:
      util.mk_or_append(self._auxs, cls.name, aux_name)


  # subtype based lookup
  @staticmethod
  def subtype_lookup(dic, ty):
    if ty in dic: return dic[ty]
    cls = class_lookup(ty)
    if not cls: return None
    if cls.itfs:
      for itf in cls.itfs:
        res = Observer.subtype_lookup(dic, itf)
        if res: return res
    if cls.sup: return Observer.subtype_lookup(dic, cls.sup)
    return None

  # find the corresponding aux type based on subtypes
  def find_aux(self, ty):
    return Observer.subtype_lookup(self._auxs, ty)

  ## @ObserverPattern(E)
  ## class C { ... }
  ## class D { ... void update(C obj1, E obj2); ... }
  ## class E { ... }
  ##   =>
  ## class C { @Subject(D, E, update) ... }
  ## class D { @Observer ... }
  ## class E { ... }
  @staticmethod
  def check_rule1(aux):
    rule = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRule1")
    rule.body = to_statements(rule, u"""
      assert subcls(belongsTo({aux.update}), {aux.observer});
      assert 1 == (argNum({aux.update}));
      assert subcls({aux.event}, argType({aux.update}, 0));
      assert {aux.subject} != {aux.observer};
    """.format(**locals()))
    aux.add_mtds([rule])

  ## @Subject(D, E, update)
  ## void M1(D obj1){}
  ## void M2(D obj2){}
  ## void M3(E obj3){}
  ##   =>
  ## List<D> _obs;
  ## void M1(D obj1) { @Attach(obj1, _obs) }
  ## void M2(D obj2) { @Detach(obj2, _obs) }
  ## void M3(E obj3) { @Handle(D, update, obj3, _obs) }
  @staticmethod
  def check_rule2(aux):
    rule = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRule2")
    rule.body = to_statements(rule, u"""
      assert subcls(belongsTo({aux.attach}), {aux.subject});
      assert subcls(belongsTo({aux.detach}), {aux.subject});
      assert subcls(belongsTo({aux.handle}), {aux.subject});
      assert 1 == (argNum({aux.attach}));
      assert 1 == (argNum({aux.detach}));
      assert 1 == (argNum({aux.handle}));
      // assert -1 == (retType({aux.attach}));
      // assert -1 == (retType({aux.detach}));
      // assert -1 == (retType({aux.handle}));
      assert {aux.attach} != {aux.detach};
      assert {aux.detach} != {aux.handle};
      assert {aux.handle} != {aux.attach};
      assert subcls({aux.observer}, argType({aux.attach}, 0));
      assert subcls({aux.observer}, argType({aux.detach}, 0));
      assert subcls({aux.event}, argType({aux.handle}, 0));
    """.format(**locals()))
    aux.add_mtds([rule])

  # assume methods that participate will be neither <init> nor static
  @staticmethod
  def is_candidate_mtd(mtd):
    return not mtd.is_init and not mtd.is_static

  # retrieve candidate methods
  @staticmethod
  def get_candidate_mtds(cls):
    mtds = cls.mtds
    if cls.is_itf and cls.subs:
      mtds = util.flatten(map(op.attrgetter("mtds"), cls.subs))
    return filter(Observer.is_candidate_mtd, mtds)

  # common params for methods in Aux...
  @staticmethod
  def mtd_params(aux):
    aname, ename = aux.name, aux.evt.name
    rcv = u'_'.join(["rcv", aname])
    return [(aname, rcv), (aname, u"arg"), (ename, u"evt")]

  # restrict call stack for the given method via a global counter
  @staticmethod
  def limit_depth(aux, mtd, depth):
    fname = mtd.name + "_depth"
    z = to_expression(u"0")
    d = Field(clazz=aux, mods=C.PRST, typ=C.J.i, name=fname, init=z)
    aux.add_flds([d])
    prologue = to_statements(mtd, u"""
      if ({fname} > {depth}) return;
      {fname} = {fname} + 1;
    """.format(**locals()))
    epilogue = to_statements(mtd, u"""
      {fname} = {fname} - 1;
    """.format(**locals()))
    mtd.body = prologue + mtd.body + epilogue

  # a method that simulates reflection
  def reflect(self, aux, clss):
    params = [(C.J.i, u"mtd_id")] + Observer.mtd_params(aux)
    reflect = Method(clazz=aux, mods=C.PBST, params=params, name=u"reflect")
    def switch( (cls, other) ):
      mtds = Observer.get_candidate_mtds(cls)
      for mtd in mtds: util.mk_or_append(self._subj_mtds, repr(mtd), aux)
      logging.debug("{}.{}, {}, {}, {}".format(aux.name, reflect.name, repr(cls), repr(other), mtds))
      def invoke(mtd):
        cls = mtd.clazz
        # if there is no implementer for this method in interface, ignore it
        if cls.is_itf and not cls.subs: return u''
        actual_params = [(other.name, u"arg")] + [params[-1]]
        args = u", ".join(sig_match(mtd.params, actual_params))
        call = u"rcv_{}.{}({});".format(aux.name, mtd.name, args)
        return u"if (mtd_id == {mtd.id}) {{ {call} }}".format(**locals())
      invocations = util.ffilter(map(invoke, mtds))
      return u"\nelse ".join(invocations)
    tests = util.ffilter(map(switch, permutations(clss, 2)))
    reflect.body = to_statements(reflect, u"\nelse ".join(tests))
    Observer.limit_depth(aux, reflect, 2)
    aux.add_mtds([reflect])
    setattr(aux, "reflect", reflect)

  # add a list of @Observer, along with an initializing statement
  @staticmethod
  def add_obs(aux, clss):
    typ = u"{}<{}>".format(C.J.LNK, aux.name)
    obs = Field(clazz=aux, typ=typ, name=C.OBS.obs)
    aux.add_flds([obs])
    setattr(aux, "obs", obs)
    tmp = '_'.join([C.OBS.tmp, aux.name])
    for cls in clss:
      if cls.is_itf: continue
      for mtd in cls.inits:
        body = u"""
          {0} {1} = ({0})this;
          {1}.{2} = new {3}();
        """.format(aux.name, tmp, C.OBS.obs, typ)
        mtd.body.extend(to_statements(mtd, body))

  # attach code
  @staticmethod
  def attach(aux):
    params = Observer.mtd_params(aux)
    attach = Method(clazz=aux, mods=C.PBST, params=params, name=u"attachCode")
    add = u"rcv_{}.{}.add(arg);".format(aux.name, C.OBS.obs)
    attach.body = to_statements(attach, add)
    aux.add_mtds([attach])
    setattr(aux, "mtd_attach", attach)

  # detach code
  @staticmethod
  def detach(aux):
    params = Observer.mtd_params(aux)
    detach = Method(clazz=aux, mods=C.PBST, params=params, name=u"detachCode")
    rm = u"rcv_{}.{}.remove(arg);".format(aux.name, C.OBS.obs)
    detach.body = to_statements(detach, rm)
    aux.add_mtds([detach])
    setattr(aux, "mtd_detach", detach)

  # handle code
  @staticmethod
  def handle(aux):
    params = Observer.mtd_params(aux)
    handle = Method(clazz=aux, mods=C.PBST, params=params, name=u"handleCode")

    cnt = Observer.__cnt
    aname = aux.name
    reflect = aux.reflect.name
    loop = u"""
      LinkedList<{aname}> obs{cnt} = rcv_{aname}._obs;
      for ({aname} o : obs{cnt}) {{
        {aname}.{reflect}({aux.update}, o, rcv_{aname}, ({aux.evt.name})evt);
      }}""".format(**locals())
    handle.body = to_statements(handle, loop)
    aux.add_mtds([handle])
    setattr(aux, "mtd_handle", handle)

  # attach/detach/handle will be dispatched here
  @staticmethod
  def subjectCall(aux):
    params = [(C.J.i, u"mtd_id")] + Observer.mtd_params(aux)
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"subjectCall")
    def switch(role):
      aname = aux.name
      v = getattr(aux, role)
      f = getattr(aux, "mtd_"+role).name
      args = ", ".join(map(lambda (ty, nm): nm, params[1:]))
      return u"if (mtd_id == {v}) {aname}.{f}({args});".format(**locals())
    roles = [C.OBS.A, C.OBS.D, C.OBS.H]
    one.body = to_statements(one, "\nelse ".join(map(switch, roles)))
    Observer.limit_depth(aux, one, 2)
    aux.add_mtds([one])
    setattr(aux, "one", one)

  ##
  ## generate an aux type for @Subject and @Observer
  ##
  def gen_aux_cls(self, event, clss):
    aux_name = self._evts[event]
    aux = merge_flat(aux_name, clss)
    aux.mods = [C.mod.PB]
    aux.subs = clss # virtual relations; to find proper methods
    setattr(aux, "evt", class_lookup(event))

    def extend_itf(cls):
      _clss = [cls]
      if cls.is_itf and cls.subs: _clss.extend(cls.subs)
      return _clss
    ext_clss = util.rm_dup(util.flatten(map(extend_itf, clss)))
    # add a list of @Observer into candidate classes
    self.add_obs(aux, ext_clss)

    # set role variables
    def set_role(role):
      setattr(aux, role, '_'.join([role, aux.name]))
    map(set_role, C.obs_roles)

    # add fields that stand for non-deterministic rule choices
    def aux_fld(init, ty, nm):
      if hasattr(aux, nm): nm = getattr(aux, nm)
      return Field(clazz=aux, mods=[C.mod.ST], typ=ty, name=nm, init=init)
    hole = to_expression(C.T.HOLE)
    aux_int = partial(aux_fld, hole, C.J.i)

    c_to_e = lambda c: to_expression(unicode(c))

    # if explicitly annotated, use those concrete event names
    if self._tmpl.is_event_annotated:
      ev_init = c_to_e(aux.evt.id)
      role_var_evt = aux_fld(ev_init, C.J.i, C.OBS.EVT)
    else: # o.w., introduce a role variable for event
      role_var_evt = aux_int(C.OBS.EVT)
    aux.add_flds([role_var_evt])
    
    ## range check
    gen_range = lambda ids: gen_E_gen(map(c_to_e, ids))
    get_id = op.attrgetter("id")

    # range check for classes
    cls_vars = [C.OBS.OBSR, C.OBS.SUBJ]
    cls_ids = map(get_id, clss)
    cls_init = gen_range(cls_ids)
    aux_int_cls = partial(aux_fld, cls_init, C.J.i)
    aux.add_flds(map(aux_int_cls, cls_vars))

    # range check for methods
    mtd_vars = [C.OBS.A, C.OBS.D, C.OBS.H, C.OBS.U]
    mtds = util.flatten(map(Observer.get_candidate_mtds, clss))
    mtd_ids = map(get_id, mtds)
    mtd_init = gen_range(mtd_ids)
    aux_int_mtd = partial(aux_fld, mtd_init, C.J.i)
    aux.add_flds(map(aux_int_mtd, mtd_vars))

    ## rules regarding non-deterministic rewritings
    Observer.check_rule1(aux)
    Observer.check_rule2(aux)

    self.reflect(aux, clss)
    Observer.attach(aux)
    Observer.detach(aux)
    Observer.handle(aux)
    Observer.subjectCall(aux)

    add_artifacts([aux.name])
    return aux

  # add an event queue
  @staticmethod
  def add_event_queue(cls):
    eq_typ = u"Queue<{}>".format(C.GUI.EVT)
    eq_name = u"_evt_queue"
    eq = Field(clazz=cls, typ=eq_typ, name=eq_name)
    cls.add_flds([eq])
    setattr(cls, "eq", eq)
    cls.init_fld(eq)

  @v.when(Template)
  def visit(self, node):
    self._tmpl = node
    if not node.events: return
    self._eq = class_lookup(C.GUI.QUE)

    # build mappings from event kinds to involved classes
    if self._tmpl.is_event_annotated:
      self.find_clss_involved_w_anno_evt(node)
    else:
      self.find_clss_involved_w_anno(node)

    # introduce AuxObserver$n$ for @Subject and @Observer
    for event in self._clss:
      clss = self._clss[event]
      node.add_classes([self.gen_aux_cls(event, clss)])

    # add an event queue
    Observer.add_event_queue(self._eq)

    # add type conversion mappings
    trimmed_auxs = {}
    for k in self._auxs: trimmed_auxs[k] = self._auxs[k][0]
    add_ty_map(trimmed_auxs)

  @v.when(Clazz)
  def visit(self, node):
    self._cur_cls = node

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    self._cur_mtd = node

    # special methods
    if node.clazz.name == C.GUI.QUE:
      eq = self._eq
      # EventQueue.dispatchEvent
      if node.name == "dispatchEvent":
        _, evt = node.params[0]

        switches = u''
        for event, i in self._tmpl.events.items():
          if event not in self._clss: continue
          clss = self._clss[event]
          cls_h = class_lookup(self._evts[event])
          cls_h_name = cls_h.name
          cls_h_lower = cls_h_name.lower()
          reflect = cls_h.reflect.name
          hdl = '.'.join([cls_h_name, cls_h.handle])
          cond_call = u"""
            else if ({evt}_k == {i}) {{
              {cls_h_name} rcv = ({cls_h_name}){evt}.getSource();
              //{cls_h_name} rcv = ({cls_h_name}){evt}._source;
              {cls_h_name}.{reflect}({hdl}, rcv, null, ({event}){evt});
            }}"""
          switches += cond_call.format(**locals())

        body = u"""
          if ({evt} == null) return;
          int {evt}_k = {evt}.kind;
          if ({evt}_k == -1) {{ // InvocationEvent
            InvocationEvent ie = (InvocationEvent){evt};
            ie.dispatch();
          }} {switches}
        """.format(**locals())
        node.body = to_statements(node, body)

      # EventQueue.getNextEvent
      elif node.name == "getNextEvent":
        body = u"if (this != null) return ({}){}.remove(); else return null;".format(node.typ, eq.eq.name)
        node.body = to_statements(node, body)

      # EventQueue.postEvent
      elif node.name == "postEvent":
        _, evt = node.params[0]
        body = u"if (this != null) {}.add({});".format(eq.eq.name, evt)
        node.body = to_statements(node, body)

      # EventQueue.invokeLater
      elif node.name == "invokeLater":
        _, r = node.params[0]
        root_evt = C.GUI.EVT
        body = u"""
          Toolkit t = @Singleton(Toolkit);
          {root_evt} evt = new InvocationEvent(null, {r});
          evt.kind = -1; // kinds of usual events start at 0
          EventQueue q = t.getSystemEventQueue();
          q.postEvent(evt);
        """.format(**locals())
        node.body = to_statements(node, body)

    # NOTE: deprecated (use adapter pattern)
    #elif node.clazz.name == C.GUI.IVK:
    #  # InvocationEvent.dispatch
    #  if node.name == "dispatch":
    #    fld = node.clazz.fld_by_typ(C.J.RUN)
    #    body = u"{}.run();".format(fld.name)
    #    node.body = to_statements(node, body)

    ## only interested in methods that appear in the samples
    #clss = util.flatten_classes([node.clazz], "subs")
    #if not sample.mtd_appears(self._smpls, clss, node.name): return

    # for methods that are candidates of @Attach/@Detach/@Handle
    if self._cur_cls.is_itf: return
    if not Observer.is_candidate_mtd(node): return
    if repr(node) in self._subj_mtds:
      cname = node.clazz.name
      evt_passed = None
      for aux in self._subj_mtds[repr(node)]:
        logging.debug("{}.{} => {}.subjectCall".format(cname, node.name, aux.name))
        if node.is_static: params = node.params
        else: params = [(cname, C.J.THIS)] + node.params
        one_params = [(C.J.i, unicode(node.id))]
        for (ty, nm) in params:
          cls_ty = class_lookup(ty)
          # downcast AWTEvent to actual event
          if aux.evt <= cls_ty:
            evt_passed = nm
            one_params.append( (aux.evt.name, nm) )
          elif self.find_aux(ty):
            one_params.append( (aux.name, nm) )
          else:
            one_params.append( (ty, nm) )

        body = u"{};".format(call_stt(aux.one, one_params))
        if evt_passed:
          body = u"""
            if ({0}_k == {1}) {{ {2} }}
          """.format(evt_passed, self._tmpl.events[aux.evt.name], body)
        node.body = to_statements(node, body) + node.body

      if evt_passed:
        k = u"int {0}_k = {0}.kind;".format(evt_passed)
        node.body = to_statements(node, k) + node.body

  @v.when(Statement)
  def visit(self, node): return [node]

  # to avoid name conflict, use fresh variables for distinct events
  __evt_cnt = 0
  @classmethod
  def fresh_evt(cls):
    cls.__evt_cnt = cls.__evt_cnt + 1
    return u"evt{}".format(cls.__evt_cnt)

  ## @React
  ##   =>
  ## AWTEvent e = q.getNextEvent();
  ## q.dispatchEvent(e);
  # NOTE: assume @React is in @Harness only; and then use variable q there
  @v.when(Expression)
  def visit(self, node):
    if node.kind == C.E.ANNO:
      _anno = node.anno
      if _anno.name == C.A.REACT:
        logging.debug("reducing: {}".format(str(_anno)))

        evt = Observer.fresh_evt()
        body = u"""
          {0} {1} = q.getNextEvent();
          q.dispatchEvent({1});
        """.format(C.GUI.EVT, evt)

        return to_statements(self._cur_mtd, body)

    return node

