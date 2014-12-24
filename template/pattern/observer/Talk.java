@ObserverPattern(Date)
public class Talk {

  Talk(int date, String title);

  void dateChanged(Date date);

  void addObserver(User user);

  void deleteObserver(User user);
 
}
