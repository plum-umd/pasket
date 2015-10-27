package pattern.state;

public class Test {

  final static String tag = Test.class.getPackage().getName();

  public static void main(String[] args) {
    System.out.println(tag + ": scenario 0");
    Test.scenario0();
    System.out.println(tag + ": scenario 1");
    Test.scenario1();
    System.out.println(tag + ": scenario 2");
    Test.scenario2();
  }

  // correct usage
  private static void scenario0() {
    Player p = new Player();
    p.prepare();
    // p.reset();
    // p.prepare();

    p.start();
    // p.reset();
    // p.prepare();
    // p.start();

    p.pause();
    // p.reset();
    // p.prepare();
    // p.start();
    // p.pause();

    p.start();
    p.stop();
    p.release();
  }

  // error 1: start w/o preparation
  private static void scenario1() {
    Player p = new Player();
    p.start();
  }

  // error 2: stop w/o starting
  private static void scenario2() {
    Player p = new Player();
    p.prepare();
    p.stop();
  }

}
