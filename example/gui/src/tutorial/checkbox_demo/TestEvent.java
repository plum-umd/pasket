package tutorial.checkbox_demo;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class TestEvent extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      click("$Glasses", true),
      click("$Teeth", true)
    );
  }

}
