from lib.typecheck import *

from ..sample import Sample

from . import is_event

@takes(str, str)
@returns(int)
def compare(org, sim):
  smpl_org = Sample(org, is_event)
  smpl_sim = Sample(sim, is_event)

  # TODO: compare two samples

  return 0

