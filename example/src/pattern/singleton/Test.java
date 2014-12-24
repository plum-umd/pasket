package pattern.singleton;

public class Test {

  final static String tag = Test.class.getPackage().getName();

  public static void main(String[] args) {
    System.out.println(tag + ": scenario 1");
    Test.scenario1();
  }

  private static void scenario1() {
    Manager m1 = Manager.getManager();
    Manager m2 = Manager.getManager(); // the same singleton
    assert (m1 == m2);
    Resource r1 = (Resource)m1.getResource(Manager.water);
    assert (r1._type == Manager.water);
    Resource r2 = (Resource)m1.getResource(Manager.power);
    assert (r2._type == Manager.power);
    Resource r3 = (Resource)m1.getResource(Manager.water); // the same singleton
    assert (r1 == r3);
  }

}
