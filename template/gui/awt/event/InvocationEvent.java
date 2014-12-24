package java.awt.event;

public class InvocationEvent extends AWTEvent {
  public InvocationEvent(Object source, Runnable runnable);
  public void dispatch();
}
