package oreilly.ch11;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class SimpleSplitPaneTest extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      setText("$Edit1", true, "some text")
    );
  }

}

