package javax.swing.text;

public abstract class AbstractDocument implements Document {
  public void addDocumentListener(DocumentListener listener);
  public void removeDocumentListener(DocumentListener listener);

  public void fireChangeUpdate(DocumentEvent e);
  public void fireInsertUpdate(DocumentEvent e);
  public void fireRemoveUpdate(DocumentEvent e);

  public int getLength();
  public String getText(int offset, int length);

  //XXX: stopgap to set the source of the event
  //public class DefaultDocumentEvent implements DocumentEvent {
  public class DefaultDocumentEvent extends EventObject implements DocumentEvent {
    //public DefaultDocumentEvent(int off, int len, DocumentEvent.EventType type);
    public DefaultDocumentEvent(int off, int len, DocumentEvent.EventType type);
    public Document getDocument();
    public DocumentEvent.EventType getType();
  }
}
