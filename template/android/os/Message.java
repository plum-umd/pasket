package android.os;

public final class Message {
  public Object obj;
  public int what;

  public Message();
  private Message(Handler h);

  @Factory
  public static Message obtain();
  @Factory
  public static Message obtain(Handler h);

  public void setTarget(Handler target);
  public Handler getTarget();
}
