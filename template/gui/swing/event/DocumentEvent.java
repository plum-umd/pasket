package javax.swing.event;

public interface DocumentEvent {
  public Document getDocument();
  public EventType getType();

  public static final class EventType {
    EventType(String s);

    public final static EventType CHANGE = new EventType("CHANGE");
    public final static EventType INSERT = new EventType("INSERT");
    public final static EventType REMOVE = new EventType("REMOVE");
  }
}
