package pattern.builder;

public class Test {

  final static String tag = Test.class.getPackage().getName();

  public static void main(String[] args) {
    System.out.println(tag + ": scenario 1");
    Test.scenario1();
  }

  /* https://talks.cs.umd.edu/lists/1?range=past */
  private static void scenario1() {
    UriBuilder builder = new UriBuilder();
    builder.scheme("https").authority("talks.cs.umd.edu");
    builder.path("lists").appendPath("1");
    builder.appendQueryParameter("range","past");
    System.out.println(builder.build());
  }

}
