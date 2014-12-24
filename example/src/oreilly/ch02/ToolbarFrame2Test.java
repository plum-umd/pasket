package oreilly.ch02;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class ToolbarFrame2Test extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      click("$Windows", true),
      click("$Mac", true)
    );
  }

}
