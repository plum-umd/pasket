package oreilly.ch12;

import gov.nasa.jpf.awt.UIActionTree;
import gov.nasa.jpf.util.event.Event;

public class ColorPicker3Test extends UIActionTree {

  @Override
  public Event createEventTree() {
    return sequence(
      click("$Show_JColorChooser", true)
    );
  }

}

