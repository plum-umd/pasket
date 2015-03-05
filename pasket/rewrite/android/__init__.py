import lib.const as C

# special cases for the accessor pattern
acc_default = [
]

# configuration for the accessor pattern
acc_conf_uni = {
  "Message": (0, 1, 1), # (get|set)Target
}

# configuration for the accessor pattern (of Map<K,V> type)
acc_conf_map = {
}

# configuration for the singleton pattern
sng_conf = [
    C.ADR.LOOP
]
