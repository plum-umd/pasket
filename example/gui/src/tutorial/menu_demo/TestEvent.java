package tutorial.menu_demo;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class TestEvent extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      click("$Both_text_and_icon", true),
      click("$A_check_box_menu_item", true)
    );
  }

}
