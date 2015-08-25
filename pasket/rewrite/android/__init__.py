import lib.const as C

# special cases for the accessor pattern
acc_default = [
  u"getHandler",
  C.ADR.ACTT, # Handler, Activity
  C.ADR.LOOP  # MessageQueue
]

# configuration for the accessor pattern
acc_conf_uni = {
  C.ADR.MSG: (1, 1, 1, False), # (get|set)Target
  C.ADR.HDL: (1, 1, 0, False), # getLooper

  C.ADR.INTT: (1, 1, 0, False), # getComponent
  C.ADR.CMP: (2, 2, 0, False), # get(Class|Package)Name

  C.ADR.VIEW: (-1, 2, 2, False), # (set|is)Enabled, (set|get)Visibility
  C.ADR.CMPB: (-1, 1, 1, False), # (set|is)Checked

  #u"InputEvent": (1, 1, 1, False), # (get|set)Source <- abstract
  u"MotionEvent": (2, 2, 1, False), # getAction(Masked)
  #u"KeyEvent": (2, 2, 1, Fasle), # getKeyCode
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  #C.ADR.BDL: (-1, 1, 1), # (get|put)*
  #C.ADR.WMG: (-1, 1, 1), # addView, findViewById
  C.ADR.SSM: (-1, 1, 1), # getService, registerService
}

# configuration for the observer pattern
obs_conf = {
  u"MotionEvent": (1, 1, 0), # no $detach
}

# configuration for the singleton pattern
sng_conf = [
  C.ADR.ACTT, # currentActivityThread
  C.ADR.LOOP, # getMainLooper
  C.ADR.WMG,  # getInstance
  C.ADR.SSM,  # getInstance
  C.ADR.TPM   # getDefault
]
