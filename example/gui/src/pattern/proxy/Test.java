package pattern.proxy;

import java.lang.reflect.Proxy;

public class Test {

  final static String tag = Test.class.getPackage().getName();

  public static void main(String[] args) {
    IStudent proxy = Test.getProxy(new Student("Jinseong Jeon"));
    System.out.println(tag + ": scenario 1");
    Test.scenario1(proxy);
  }

  private static IStudent getProxy(IStudent student) {
    return (IStudent)Proxy.newProxyInstance(
      student.getClass().getClassLoader(),
      student.getClass().getInterfaces(),
      new AccessController(student));
  }

  private static void scenario1(IStudent student) {
    System.out.println("Profile: " + student.getProfile());
    // A student cannot set his or her grade.
    student.setGrade(4);
    System.out.println("Grade: " + student.getGrade());
    // Profile will be loaded only once.
    System.out.println("Profile: " + student.getProfile());
  }

}
