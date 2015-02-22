import logging

from lib.typecheck import *
import lib.const as C

from .. import util

from accessor_adhoc import AccessorAdHoc
from accessor_uni import AccessorUni
from builder import Builder
from factory import Factory
from proxy import Proxy
from singleton import Singleton
from state import State

@takes(str, list_of("Sample"), "Template", list_of(str))
@returns(nothing)
def visit(cmd, smpls, tmpl, patterns):
  p2v = {}

  ## structural patterns

  p2v[C.P.BLD] = Builder(smpls)

  p2v[C.P.FAC] = Factory(smpls)

  p2v[C.P.SNG] = Singleton(smpls)

  if cmd == "android": pass
  elif cmd == "gui":
    from gui import acc_default, acc_conf_uni
    p2v[C.P.ACCA] = AccessorAdHoc(smpls, acc_default)
    p2v[C.P.ACCU] = AccessorUni(smpls, acc_default, acc_conf_uni)
  else:
    p2v[C.P.ACCA] = AccessorAdHoc(smpls)

  ## behavioral patterns

  if cmd == "android": pass
  elif cmd == "gui":
    from gui.observer import Observer
    p2v[C.P.OBS] = Observer(smpls)
  else:
    from observer import Observer
    p2v[C.P.OBS] = Observer(smpls)

  p2v[C.P.PRX] = Proxy(smpls)

  p2v[C.P.STA] = State(smpls)

  keys = p2v.keys()
  if not patterns: # then try all the patterns
    patterns = keys

  # filter out unknown pattern names
  patterns = util.intersection(patterns, keys)
  # sort so that visitors can be visited in the order of generation
  patterns.sort()

  for p in patterns:
    logging.info("rewriting {} pattern".format(p))
    tmpl.accept(p2v[p])

