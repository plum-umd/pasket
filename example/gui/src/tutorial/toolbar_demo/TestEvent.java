package tutorial.toolbar_demo;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class TestEvent extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      click("$Next", true),
      click("$Previous", true)
    );
  }

}
