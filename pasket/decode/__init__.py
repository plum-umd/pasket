import os
import operator as op
import logging

from lib.typecheck import *
import lib.const as C

from .. import util
from ..meta import class_lookup
from ..meta.template import Template
from ..meta.clazz import Clazz
from ..meta.method import Method

from ..analysis.empty import EmptyFinder
from collection import Collection
from observer import Observer
from accessor import Accessor
from singleton import Singleton

pkgs_android = [u"android."]

pkgs_gui = [u"java.awt", u"javax.swing", u"javax.accessibility"]

# white-list checking
@takes(unicode, list_of(unicode))
@returns(bool)
def check_pkg(pname, lst):
  return util.exists(lambda pkg: pname.startswith(pkg), lst)


# Android-specific trimming
@takes(Template)
@returns(nothing)
def trim_model_android(tmpl):
  for cls in tmpl.classes[:]:
    if cls.pkg and check_pkg(cls.pkg, pkgs_android): continue
    logging.debug("trimming: {}".format(cls.name))
    tmpl.classes.remove(cls)


# Swing-specific trimming
@takes(Template)
@returns(nothing)
def trim_model_gui(tmpl):
  for cls in tmpl.classes[:]:
    if cls.pkg and check_pkg(cls.pkg, pkgs_gui): continue
    # special case: java.util.EventObject
    if C.GUI.EVT in cls.name: continue
    # o.w. trim
    logging.debug("trimming: {}".format(cls.name))
    tmpl.classes.remove(cls)

  # introduce aux class/interface for the sanity checker
  hdl_itf = Clazz(name=u"EventHandler", kind=C.T.ITF)
  hdl_params = [(C.J.STR, u"line")]
  hdl_mtd = Method(clazz=hdl_itf, name=u"handleEvent", params=hdl_params)
  hdl_itf.add_mtds([hdl_mtd])

  tmpl.add_classes([hdl_itf])


# general trimming
@takes(Template)
@returns(nothing)
def trim_model_pattern(tmpl):
  # add main() if not exists
  tmpl.add_main()


# build folders for the given package name
# e.g., for x.y, generate x and then y under x if not exist
@takes(str, unicode)
@returns(nothing)
def build_pkg_folders(java_dir, pkg):
  p = java_dir
  for elt in pkg.split('.'):
    p = os.path.join(p, elt)
    if not os.path.exists(p):
      os.makedirs(p)


# find appropriate import statements, generally
@takes(str, unicode, list_of(unicode))
@returns(list_of(unicode))
def find_imports(body, pkg, clss):
  def appear(cls): return cls in body
  return [ '.'.join([pkg, cls]) for cls in filter(appear, clss) ]


# merge two tmpl instances in tmpls into one
def merge_tmpls(prv, elt):
  tmpl1, p2v1 = prv # accumulated
  tmpl2, p2v2 = elt # newly visited
  if not tmpl1 or p2v1 == {}: # reduce() visits this function first time
    logging.info("merging " + p2v2[C.P.OBS].demo)
    return elt
  logging.info("with " + p2v2[C.P.OBS].demo)

  tmpl, p2v = tmpl1, p2v1 # to be merged
  tmpl.unfreeze()

  # merging the observer pattern
  obs1, obs2 = p2v1[C.P.OBS], p2v2[C.P.OBS]
  evts = obs1.evts.values()
  attrs = ["subj", "obsr", "evts", "attach", "detach", "handle"]
  for aux2 in obs2.evts.keys():
    evt = obs2.evts[aux2]
    if evt in evts:
      logging.debug("{} is already solved".format(evt.name))
      def aux_finder(aux): return obs1.evts[aux] == evt
      aux1 = util.find(aux_finder, obs1.evts.keys())
      subj1 = obs1.subj[aux1]
      subj2 = obs2.subj[aux2]
      if subj1.name == subj2.name:
        try:
          for attr in attrs:
            obj1 = getattr(obs1, attr)[aux1]
            obj2 = getattr(obs2, attr)[aux2]
            assert obj1.name == obj2.name
        except AssertionError:
          logging.error("solution conflict on {}".format(attr))
          logging.error("{} != {}".format(obj1.name, obj2.name))
          raise Exception

    else:
      logging.debug("{} is a new event type".format(evt.name))

      def get_role(attr): return getattr(obs2, attr)[aux2]
      attach, detach = map(get_role, ["attach", "detach"])
      subj2 = obs2.subj[aux2]

      for aux1 in obs1.evts.keys():
        subj1 = obs1.subj[aux1]
        # same @Subject for different event types
        if subj1.name == subj2.name:
          logging.debug("{}: same subject: {}".format(evt.name, subj2.name))

          obsr1, obsr2 = obs1.obsr[aux1], obs2.obsr[aux2]
          if obsr1.name == obsr2.name:
            logging.debug("{}: even same observer: {}".format(evt.name, obsr1.name))
          else:
            # add List<@Observer> into @Subject if not exist
            if subj1.add_fld(subj2.obs): subj1.init_fld(subj2.obs)
            # add @Attach/@Detach into @Subject if not exist
            subj1.add_mtd(attach)
            subj1.add_mtd(detach)
            # merge @Handle if conflict
            if subj1.handle.name == subj2.handle.name:
              subj1.handle.body += subj2.handle.body
            else:
              subj1.add_mtd(subj2.handle)

          break

      # copy role mappings
      def cp_role(attr):
        prv_dict, elt_dict = map(op.attrgetter(attr), [obs1, obs2])
        prv_dict[aux2] = elt_dict[aux2]
      map(cp_role, attrs)

  # merging the accessor pattern
  #acc1, acc2 = p2v1[C.P.ACC], p2v2[C.P.ACC]

  # merge classes
  for cls2 in tmpl2.classes:
    if cls2.name == C.J.OBJ: continue # skip Object
    cls1 = class_lookup(cls2.name)
    # TODO: this case never happens now because we don't use reducer.remove_cls
    if not cls1: tmpl.classes.append(cls2)
    else: cls1.merge(cls2)

  tmpl.freeze()
  return (tmpl, p2v)


# translate high-level templates into Java code
# according to the low-level synthesis result
@takes(str, str, list_of(Template), list_of(str), list_of(str))
@returns(nothing)
def to_java(cmd, java_dir, tmpls, output_paths, patterns):
  ## clean up result directory
  if os.path.isdir(java_dir): util.clean_dir(java_dir)
  else: os.makedirs(java_dir)

  ## interpret synthesis result per demo
  p2vs = []
  logging.info("merging {} template(s)".format(len(tmpls)))
  for tmpl, output_path in zip(tmpls, output_paths):
    tmpl.unfreeze()
    demo = util.pure_base(output_path)

    _patterns = patterns[:]
    p2v = {}
    p2v[C.P.OBS] = Observer(output_path)

    if cmd == "android": pass
    elif cmd == "gui":
      from ..rewrite.gui import acc_conf_uni
      p2v[C.P.ACC] = Accessor(output_path, acc_conf_uni)
    else: pass

    p2v[C.P.SNG] = Singleton(output_path)

    keys = p2v.keys()
    if not _patterns: # then try all the patterns
      _patterns = keys

    ## filter out unknown pattern names
    _patterns = util.intersection(_patterns, keys)

    coll = "collection"
    p2v[coll] = Collection()
    _patterns.insert(0, coll)
    
    p2vs.append(p2v)
    
    for p in _patterns:
      if p not in p2v: continue
      logging.info("decoding {} pattern for {}".format(p, demo))
      tmpl.accept(p2v[p])

    tmpl.freeze()

  ## merge multiple synthesis results
  tmpl, _ = reduce(merge_tmpls, zip(tmpls, p2vs), (None, {}))

  ## statistics
  counter = EmptyFinder()
  tmpl.accept(counter)
  logging.info("classes: {}".format(counter.cls_count))
  logging.info("methods: {} (empty: {})".format(counter.mtd_count, counter.empty_count))

  ## framework-specific trimming of models
  f = globals()["trim_model_" + cmd]
  f(tmpl)

  dump(cmd, java_dir, tmpl, "decoding")


# dump out the given template, which might be
# either an intermediate AST or the final model
@takes(str, str, Template, optional(str))
@returns(nothing)
def dump(cmd, dst_dir, tmpl, msg=None):

  def write_imports(imports):
    def write_import(i): return "import {};".format(i)
    return '\n'.join(map(write_import, imports)) + '\n'

  ios = [u"File", u"InputStream", u"FileInputStream", \
      u"InputStreamReader", u"BufferedReader", \
      u"FileNotFoundException", u"IOException"]

  gui_pkgs = set([])
  for cls in tmpl.classes:
    if not cls.pkg: continue
    if check_pkg(cls.pkg, pkgs_gui): gui_pkgs.add(cls.pkg)

  for cls in tmpl.classes:
    ## generate folders according to package hierarchy
    fname = cls.name + ".java"
    if cls.pkg:
      build_pkg_folders(dst_dir, cls.pkg)
      folders = [dst_dir] + cls.pkg.split('.') + [fname]
      java_path = os.path.join(*folders)
    else: java_path = os.path.join(dst_dir, fname)

    ## figure out import statements
    imports = []

    cls_body = str(cls)
    imports.extend(find_imports(cls_body, u"java.util", C.collections))
    imports.extend(find_imports(cls_body, u"java.io", ios))

    if cmd == "android":
      pass
    elif cmd == "gui":
      imports.extend(find_imports(cls_body, u"java.util", [C.GUI.EVT]))
      for pkg in gui_pkgs:
        if not cls.pkg or cls.pkg != pkg: imports.append(pkg+".*")

    ## generate Java files
    with open(java_path, 'w') as f:
      if cls.pkg: f.write(C.T.PKG + ' ' + cls.pkg + ";\n")
      f.write(write_imports(imports))
      f.write(cls_body)
      if msg: logging.info(" ".join([msg, f.name]))
      else: logging.debug("dumping " + f.name)

