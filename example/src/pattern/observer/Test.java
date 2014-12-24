package pattern.observer;

public class Test {

  final static String tag = Test.class.getPackage().getName();

  public static void main(String[] args) {
    System.out.println(tag + ": scenario 1");
    Test.scenario1();
    System.out.println(tag + ": scenario 2");
    Test.scenario2();
    System.out.println(tag + ": scenario 3");
    Test.scenario3();
  }

  // one talk, many users
  private static void scenario1() {
    Talk t = new Talk(153, "Dr. Android and Mr. Hide");
    User[] users = {
      new User("Jeff"),
      new User("Armando")
    };

    for (int i = 0; i < users.length; i++)
      t.addObserver(users[i]);

    for (int i = 152; i < 155; i++) {
      t.dateChanged(new Date(i));
    }
  }

  // many talks, one user
  private static void scenario2() {
    User l = new User("Lukas");
    Talk[] talks = {
      new Talk(80, "How movies teach manhood"),
      new Talk(79, "Steve Jobs: How to live before you die")
    };

    for (int i = 0; i < talks.length; i++)
      talks[i].addObserver(l);

    for (int i = 78; i < 81; i++) {
      Date d = new Date(i);
      for (int j = 0; j < talks.length; j++)
        talks[j].dateChanged(d);
    }
  }

  // never update the detached observer
  private static void scenario3() {
    User l = new User("Lucia");
    Talk t = new Talk(38, "Looks aren't everything");

    t.addObserver(l);
    t.dateChanged(new Date(38));
    t.deleteObserver(l);
    t.dateChanged(new Date(38));
  }

}
