package tutorial.toolbar_demo2;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class TestEvent extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      click("$Other", true),
      click("$Next", true)
    );
  }

}
