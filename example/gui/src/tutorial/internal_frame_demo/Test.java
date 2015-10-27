package tutorial.internal_frame_demo;

public class Test {

  final static String tag = Test.class.getPackage().getName();

  public static void main(String[] args) {
    System.out.println(tag);
    InternalFrameDemo.main();
  }

}
