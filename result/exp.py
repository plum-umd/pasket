#!/usr/bin/env python

import datetime
import os
import subprocess
import sys

demos = {
  "android": ["button", "checkbox", "telephony_manager"],
  "gui": ["checkbox_demo", "colorchooser_demo", "combobox_demo", "custom_icon_demo", "filechooser_demo", "toolbar_demo", "button_demo", "menu_demo", "splitpane_divider_demo", "text_field_demo"]
}

output = "output"

def main():
  opts = []
  opts.extend(["--fe-tempdir", os.path.join(".", "tmp")])
  opts.extend(["--slv-timeout", "30"])
  opts.extend(["--slv-parallel", "--slv-randassign", "--slv-strategy", "WILCOXON"])
  opts.extend(["--slv-p-cpus", "32"])
  opts.extend(["--slv-ntimes", str(1024*128)])

  r_cmds = []
  r_cmds.extend(["sketch"])
  r_cmds.extend(opts)
  for cmd in demos:
    tutorials = demos[cmd]
    for i in xrange(7):
      for tutorial in tutorials:
        _r_cmds = r_cmds[:]
        dp = "sk_{}".format(tutorial)
        _r_cmds.extend(["--fe-inc", dp])
        _r_cmds.extend([os.path.join(dp, "sample.sk")])
        print " ".join(_r_cmds)
        now = int(datetime.datetime.now().strftime("%H%M%S"))
        op = os.path.join(output, "{}_{}.txt".format(tutorial, now))
        with open(op, 'w') as f:
          try:
            subprocess.check_call(_r_cmds, stdout=f)
          except subprocess.CalledProcessError:
            print "not finished properly: {} {}".format(cmd, tutorial)


if __name__ == "__main__":
  sys.exit(main())

