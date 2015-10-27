package pattern.observer;

import java.util.Observer;
import java.util.Observable;

class Talk extends Observable {

  int _date;
  String _title;

  public Talk (int date, String title) {
    this._date = date;
    this._title = title;
  }

  // to avoid copy constructor of Date, directly access to date._date
  public void dateChanged(Date date) {
    System.out.println("Today is " + date._date);
    if (0 == this._date - date._date) {
      setChanged();
      notifyObservers(date);
    }
  }

  // to capture system API
  public void addObserver(Observer o) {
    super.addObserver(o);
  }

  // to capture system API
  public void deleteObserver(Observer o) {
    super.deleteObserver(o);
  }

}
