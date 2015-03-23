import copy as cp
import operator as op
from functools import partial
import logging

import lib.const as C
import lib.visit as v

from .. import add_artifacts
from .. import util
from .. import sample
from ..harness import gen_events
from ..reducer import add_getter
from ..encoder import add_ty_map
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz, merge_flat
from ..meta.method import Method, sig_match, call_stt
from ..meta.field import Field
from ..meta.statement import Statement, to_statements
from ..meta.expression import Expression, to_expression

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
    self._main_cls = None
    self._cur_cls = None
    self._cur_mtd = None
    # classes that are involved in this pattern
    self._clss = {} # { E1: [C1, D1], E2: [C2, D2], ... }
    # events to be handled
    self._evts = {} # { C1: E1, D1: E1, C2: E2, D2: E2, ... }
    # aux class names
    self._auxs = {} # { C1: Aux1, D1: Aux1, C2: Aux2, D2: Aux2, ... }

  @v.on("node")
  def visit(self, node):
    """
    This is the generic method to initialize the dynamic dispatcher
    """

  # find possible classes for Subject and Observer
  # so as to build self._clss and self._auxs
  # at this point, assume those are annotated with @ObserverPattern(E+)
  def find_clss_involved(self, tmpl):
    for cls in tmpl.classes:
      if util.exists(Observer.find_obs(), cls.annos):
        # ignore interface without implementers
        if cls.is_itf and not cls.subs:
          logging.debug("ignore {} due to no implementers".format(cls.name))
          continue

        events = util.find(Observer.find_obs(), cls.annos).events
        for event in events:
          if event in self._clss: self._clss[event].append(cls)
          else: self._clss[event] = [cls]
          self._evts[cls.name] = event

    for event in self._clss.keys():
      # if # of candidates is less than 2, ignore that event
      if len(self._clss[event]) < 2:
        logging.debug("ignore {} {}".format(event, self._clss[event]))
        del self._clss[event]
        del tmpl.events[event]
        continue

      aux_name = Observer.new_aux()
      tmpl.obs_auxs[aux_name] = self._clss[event]
      logging.debug("{}: {} {}".format(event, aux_name, self._clss[event]))
      for cls in self._clss[event]:
        self._auxs[cls.name] = aux_name

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
      assert subcls({aux.observer}, belongsTo({aux.update}));
      assert 2 == (argNum({aux.update}));
      assert subcls({aux.subject}, argType({aux.update}, 0));
      assert subcls({aux.event}, argType({aux.update}, 1));
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
      assert subcls({aux.subject}, belongsTo({aux.attach}));
      assert subcls({aux.subject}, belongsTo({aux.detach}));
      assert subcls({aux.subject}, belongsTo({aux.handle}));
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
    d = Field(clazz=aux, mods=[C.mod.PR, C.mod.ST], typ=C.J.i, name=fname, init=z)
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
  @staticmethod
  def reflect(aux, clss):
    params = [(C.J.i, u"mtd_id")] + Observer.mtd_params(aux)
    reflect = Method(clazz=aux, mods=C.PBST, params=params, name=u"reflect")
    def switch( (cls, other) ):
      mtds = Observer.get_candidate_mtds(cls)
      logging.debug("{}.{} {}".format(aux.name, reflect.name, mtds))
      def invoke(mtd):
        cls = mtd.clazz
        # if there is no implementer for this method in interface, ignore it
        if cls.is_itf and not cls.subs: return u''
        actual_params = [(other.name, u"arg")] + [params[-1]]
        args = ", ".join(sig_match(mtd.params, actual_params))
        call = "rcv_{}.{}({});".format(aux.name, mtd.name, args)
        return u"if (mtd_id == {mtd.id}) {{ {call} }}".format(**locals())
      invocations = filter(None, map(invoke, mtds))
      return "\nelse ".join(invocations)
    tests = filter(None, map(switch, zip(clss, reversed(clss))))
    reflect.body = to_statements(reflect, u"\nelse ".join(tests))
    Observer.limit_depth(aux, reflect, 2)
    aux.add_mtds([reflect])
    setattr(aux, "reflect", reflect)

  # add a list of @Observer, along with an initializing statement
  @staticmethod
  def add_obs(aux, clss):
    typ = u"{}<{}>".format(C.J.LST, C.J.OBJ)
    obs = Field(clazz=aux, typ=typ, name=C.OBS.obs)
    aux.add_flds([obs])
    setattr(aux, "obs", obs)
    for cls in clss:
      if cls.is_itf: continue
      for mtd in cls.inits:
        body = u"""
          {0} {1} = ({0})this;
          {1}.{2} = new {3}();
        """.format(aux.name, C.OBS.tmp, C.OBS.obs, typ)
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

    # currently, compare the fields with the same name
    def gen_cond(v, cls):
      get_name = op.attrgetter("name")
      evt_flds = set(map(get_name, aux.evt.flds))
      cls_flds = set(map(get_name, cls.flds))
      common = list(evt_flds & cls_flds)
      def wrap_w_cmp(v, fname):
        fld = cls.fld_by_name(fname)
        if fld.typ == C.J.STR:
          cmp_tmpl = "@CompareString({{ {v}.{fname}, evt.{fname} }})"
        else:
          cmp_tmpl = "@Compare({{ {v}.{fname}, evt.{fname} }})"
        return cmp_tmpl.format(**locals())
      def conjunct(cmp1, cmp2): return cmp1+" && "+cmp2
      return reduce(conjunct, map(partial(wrap_w_cmp, v), common), "true")

    cond = gen_cond("rcv_"+aux.name, aux)
    aname = aux.name
    reflect = aux.reflect.name
    loop = u"""
      List<Object> obs = rcv_{aname}._obs;
      for ({aname} o : obs) {{
        if ({cond}) {{
          {aname}.{reflect}({aux.update}, o, rcv_{aname}, evt);
        }}
      }}""".format(**locals())
    handle.body = to_statements(handle, loop)
    aux.add_mtds([handle])
    setattr(aux, "mtd_handle", handle)

  # attach/detach/handle will be dispatched here
  @staticmethod
  def all_in_one(aux):
    params = [(C.J.i, u"mtd_id")] + Observer.mtd_params(aux)
    one = Method(clazz=aux, mods=C.PBST, params=params, name=u"allInOne")
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
    aux_name = self._auxs[clss[0].name]
    aux = merge_flat(aux_name, clss)
    aux.mods = [C.mod.PB]
    aux.subs = clss # virtual relations; to find proper methods
    setattr(aux, "evt", class_lookup(event))

    def extend_itf(cls):
      clss = [cls]
      if cls.is_itf and cls.subs: clss.extend(cls.subs)
      return clss
    ext_clss = util.flatten(map(extend_itf, clss))
    # add a list of @Observer
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
    #aux_str = partial(aux_fld, hole, C.J.STR)
    roles_ex_evt = C.obs_roles[:]
    roles_ex_evt.remove(C.OBS.EVT)
    annos = map(aux_int, roles_ex_evt)
    ev_init = to_expression(unicode(aux.evt.id))
    anno_ev = aux_fld(ev_init, C.J.i, C.OBS.EVT)
    aux.add_flds(annos + [anno_ev])
    
    # range check
    rg_chk = Method(clazz=aux, mods=[C.mod.ST, C.mod.HN], name=u"checkRange")
    get_id = op.attrgetter("id")
    cls_ids = map(get_id, clss)
    mtds = util.flatten(map(Observer.get_candidate_mtds, clss))
    mtd_ids = map(get_id, mtds)
    def aux_range(nm, ids):
      eqs = map(lambda i: getattr(aux, nm)+" == "+str(i), ids)
      return u"assert " + reduce(lambda x, y: x+" || "+y, eqs) + ";"
                     
    cls_vars = [C.OBS.OBSR, C.OBS.SUBJ]
    mtd_vars = [C.OBS.A, C.OBS.D, C.OBS.H, C.OBS.U]
    checkers = map(lambda c: aux_range(c, cls_ids), cls_vars) \
             + map(lambda m: aux_range(m, mtd_ids), mtd_vars)
    rg_chk.body = to_statements(rg_chk, '\n'.join(checkers))
    aux.add_mtds([rg_chk])
    
    Observer.check_rule1(aux)
    Observer.check_rule2(aux)

    Observer.reflect(aux, clss)
    Observer.attach(aux)
    Observer.detach(aux)
    Observer.handle(aux)
    Observer.all_in_one(aux)

    add_artifacts([aux.name])
    return aux

  # add an event queue into the main class
  @staticmethod
  def add_event_queue(cls):
    eq_typ = u"Queue<Event>"
    eq_name = u"_evt_queue"
    eq = Field(clazz=cls, mods=[C.mod.ST], typ=eq_typ, name=eq_name)
    cls.add_flds([eq])
    setattr(cls, "eq", eq)
    cls.clinit_fld(eq)
    add_getter(cls, eq, u"getEventQueue")

  # define Dispatcher class and add dispatcher mappings into the main class
  def add_dispatchers(self, tmpl):
    # class Dispatcher { AuxObserver$n$ hdl$n$; }
    cls_d = Clazz(mods=[C.mod.PB], name=u"Dispatcher")
    cls_d.add_default_init()
    for event in self._clss:
      clss = self._clss[event]
      aux_name = self._auxs[clss[0].name]
      fld_h = Field(clazz=cls_d, typ=aux_name, name=aux_name.lower())
      cls_d.add_flds([fld_h])
    tmpl.add_classes([cls_d])
    add_artifacts([cls_d.name])

    main_cls = tmpl.main_cls

    # mappings from event kinds to dispatchers
    dp_typ = u"Map<Integer, List<Dispatcher>>"
    dp_name = u"_dispatchers"
    dp = Field(clazz=main_cls, mods=[C.mod.ST], typ=dp_typ, name=dp_name)
    main_cls.add_flds([dp])
    setattr(main_cls, "dp", dp)
    main_cls.clinit_fld(dp)
    add_getter(main_cls, dp, u"getDispatchers")

    # a method to add an instance of Dispatcher into dispatchers
    params = [(C.J.i, u"kind"), (cls_d.name, u"dp")]
    dp_adder = Method(clazz=main_cls, mods=C.PBST, name=u"addDispatcher", params=params)
    body = u"""
      List<Dispatcher> l = {dp_name}.get(kind);
      if (l == null) {{
        l = new List<Dispatcher>();
        {dp_name}.put(kind, l);
      }}
      l = {dp_name}.get(kind);
      l.add(dp);
    """.format(**locals())
    dp_adder.body = to_statements(dp_adder, body)
    main_cls.add_mtds([dp_adder])
    setattr(dp, "adder", dp_adder)

  # code snippets to set environment changes
  @staticmethod
  def set_env_changes(smpl, tmpl, mtd):
    eq = tmpl.main_cls.eq.name
    dp = tmpl.main_cls.dp.name
    body = u"{dp}.clear();\n".format(**locals())
    body += gen_events(tmpl, smpl, u"{}.add".format(eq))
    mtd.body = to_statements(mtd, body) + mtd.body

  @v.when(Template)
  def visit(self, node):
    self._tmpl = node
    if not node.events: return
    self._main_cls = node.main_cls

    # build mappings from event kinds to involved classes
    self.find_clss_involved(node)

    # introduce AuxObserver$n$ for @Subject and @Observer
    for event in self._clss:
      clss = self._clss[event]
      node.add_classes([self.gen_aux_cls(event, clss)])

    # add an event queue into the main class
    Observer.add_event_queue(node.main_cls)

    # define Dispatcher class and add dispatcher mappings into the main class
    self.add_dispatchers(node)

    # add code snippets to set env. changes into @Harness methods
    for smpl in self._smpls:
      if not smpl.evts: continue
      Observer.set_env_changes(smpl, node, node.harness(smpl.name))

    # add type conversion mappings
    add_ty_map(self._auxs)

  @v.when(Clazz)
  def visit(self, node):
    self._cur_cls = node

  @v.when(Field)
  def visit(self, node): pass

  @v.when(Method)
  def visit(self, node):
    self._cur_mtd = node
    ## only interested in methods that appear in the samples
    #clss = util.flatten_classes([node.clazz], "subs")
    #if not sample.mtd_appears(self._smpls, clss, node.name): return

    # for constructors that are candidates of @Subject
    if node.is_init and node.typ in self._auxs:
      # Dispatcher dp$n$ = new Dispatcher();
      dp_cls = u"Dispatcher"
      dp = Observer.fresh_dp()

      # dp$n$ = this;
      aux = class_lookup(self._auxs[node.typ])
      aux_lower = aux.name.lower()
      v = C.J.THIS

      # Main.addDispatcher(kind, dp$n$);
      main_cls = self._main_cls.name
      dp_adder = self._main_cls.dp.adder.name
      kind = self._tmpl.events[self._evts[node.typ]]

      # checking whether Ty is subtype of @Subject will be done dynamically
      # if (cls_id <= AuxObserver$n$.subject) { ... }
      cls_id = class_lookup(node.typ).id
      body = u"""
        if (subcls({cls_id}, {aux.name}.{aux.subject})) {{
          {dp_cls} {dp} = new {dp_cls}();
          {dp}.{aux_lower} = {v};
          {main_cls}.{dp_adder}({kind}, {dp});
        }}""".format(**locals())
      node.body += to_statements(node, body)

    # for methods that are candidates of @Attach/@Detach/@Handle
    if self._cur_cls.is_itf: return
    if not Observer.is_candidate_mtd(node): return
    if node.clazz.name in self._evts:
      cname = node.clazz.name
      aux = class_lookup(self._auxs[cname])
      logging.debug("{}.{} => {}.allInOne".format(cname, node.name, aux.name))
      if node.is_static: params = node.params
      else: params = [(cname, C.J.THIS)] + node.params
      one_params = [(C.J.i, unicode(node.id))]
      for (ty, nm) in params:
        if ty in self._evts: one_params.append( (aux.name, nm) )
        else: one_params.append( (ty, nm) )
      body = u"{};".format(call_stt(aux.one, one_params))
      node.body = to_statements(node, body) + node.body

  # to avoid name conflict, use fresh variables for distinct dispatchers
  __dp_cnt = 0
  @classmethod
  def fresh_dp(cls):
    cls.__dp_cnt = cls.__dp_cnt + 1
    return u"dp{}".format(cls.__dp_cnt)

  @v.when(Statement)
  def visit(self, node): return [node]

  # to avoid name conflict, use fresh variables for distinct events
  __evt_cnt = 0
  @classmethod
  def fresh_evt(cls):
    cls.__evt_cnt = cls.__evt_cnt + 1
    return u"evt{}".format(cls.__evt_cnt)

  # replace @React with an event handling loop
  @v.when(Expression)
  def visit(self, node):
    if node.kind == C.E.ANNO:
      _anno = node.anno
      if _anno.name == C.A.REACT:
        logging.debug("reducing: {}".format(str(_anno)))

        evt = Observer.fresh_evt()
        eq = self._main_cls.eq.name
        dp = self._main_cls.dp.name

        switches = u''
        for event, i in self._tmpl.events.iteritems():
          clss = self._clss[event]
          cls_h = class_lookup(self._auxs[clss[0].name])
          cls_h_name = cls_h.name
          cls_h_lower = cls_h_name.lower()
          reflect = cls_h.reflect.name
          hdl = '.'.join([cls_h_name, cls_h.handle])
          fid = event.lower()
          cond_call = u"""
            if ({evt}_k == {i}) {{
              List<Dispatcher> objs = {dp}.get({evt}_k);
              for (Dispatcher obj : objs) {{
                {cls_h_name} rcv = obj.{cls_h_lower};
                {cls_h_name}.{reflect}({hdl}, rcv, null, {evt}.{fid});
              }}
            }}"""
          switches += cond_call.format(**locals())

        body = u"""
          if (!{eq}.isEmpty()) {{
            Event {evt} = {eq}.remove();
            int {evt}_k = {evt}.kind;
            {switches}
          }}""".format(**locals())
        return to_statements(self._cur_mtd, body)

    return node

