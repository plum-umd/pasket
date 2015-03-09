import lib.const as C

# special cases for the accessor pattern
acc_default = [
  C.ADR.ACTT, # Handler
  C.ADR.LOOP  # MessageQueue
]

# configuration for the accessor pattern
acc_conf_uni = {
  "Message": (0, 1, 1), # (get|set)Target
  "Handler": (1, 1, 0), # getLooper
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
  "Bundle": (0, 1, 1), # (get|put)*
  "Context": (0, 1, 0), # getSystemService
}

# configuration for the singleton pattern
sng_conf = [
  C.ADR.ACTT,
  C.ADR.LOOP
]
