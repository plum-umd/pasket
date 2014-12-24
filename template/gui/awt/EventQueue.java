package java.awt;

public class EventQueue {
  protected void dispatchEvent(EventObject event);
  public EventObject getNextEvent();
  public void postEvent(EventObject event);

  public static void invokeLater(Runnable runnable);
  //public static void invokeAndWait(Runnable runnable);
}
