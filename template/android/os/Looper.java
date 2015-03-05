package android.os;

//@Singleton
public final class Looper {
  public static Looper getMainLooper();
  public static void prepareMainLooper();
  public static void loop();
}
