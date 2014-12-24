public class Simulator {{

  static EventHandler hdl = null;
  static EventHandler getEventHandler(Adapted{demo} d) {{
    if (hdl == null)
      hdl = new EventHandler(d);
    return hdl;
  }}

  public static void simulate(String[] events) {{
    Adapted{demo}.main();
    Adapted{demo} current = Adapted{demo}.get{demo}();
    EventHandler handler = getEventHandler(current);
    for (int i = 0; i < events.length; i++) {{
      handler.handleEvent(events[i]);
    }}
  }}

  // scenario :== a list of events
  static String[][] scenarios = {scenarios};

  public static void main(String[] args) {{
    for (int i = 0; i < scenarios.length; i++) {{
      simulate(scenarios[i]);
    }}
  }}

}}
