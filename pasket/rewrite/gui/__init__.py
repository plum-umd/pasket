import lib.const as C

# special cases for the accessor pattern
acc_default = [
    C.GUI.TOOL,
    "JColorChooser", # ColorSelectionModel
    "JTextComponent", # Document
    "JMenuItem", "JMenu" # AccessibleContext
]

# configuration for the accessor pattern
acc_conf_uni = {
  "EventObject": (1, 1, 0), # getSource
  "InvocationEvent": (2, 0, 0), # to set Runnable

  "ActionEvent": (3, 1, 0), # getActionCommand
  "ItemEvent": (4, 2, 0), # getItemSelectable/getStateChange

  "JButton": (2, 1, 1), # (get|set)ActionCommand
}

