package pattern.observer;

import java.util.Observer;
import java.util.Observable;

class User implements Observer {

  String _name;

  public User (String name) {
    this._name = name;
  }

  public void update(Observable o, Object arg) {
    if (o instanceof Talk) {
      Talk talk = (Talk)o;
      String msg = this._name + " is ";
      if (Math.random() < 0.25) {
        msg += "busy; won't go to ";
      } else {
        msg += "going to attend ";
      }
      msg += "the talk entitled \"" + talk._title + "\"";
      System.out.println(msg);
    }
  }

}
