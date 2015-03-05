package android.app;

public final class ActivityThead {
  public static void main(String[] args) {
    Looper.prepareMainLooper();
    Looper.loop();
  }
}
