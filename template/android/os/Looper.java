package android.os;

//@Singleton
public final class Looper {
  public static Looper getMainLooper();
  public final MessageQueue myQueue();

  public static void prepareMainLooper();
  public static void loop();
}
