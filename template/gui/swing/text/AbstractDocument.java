package javax.swing.text;

public abstract class AbstractDocument implements Document {
  public void addDocumentListener(DocumentListener listener);
  public void removeDocumentListener(DocumentListener listener);

  protected void fireChangeUpdate(DocumentEvent e);
  protected void fireInsertUpdate(DocumentEvent e);
  protected void fireRemoveUpdate(DocumentEvent e);

  public int getLength();
  public String getText(int offset, int length);

  public class DefaultDocumentEvent implements DocumentEvent {
    public DefaultDocumentEvent(int off, int len, DocumentEvent.EventType type);
    public Document getDocument();
    public DocumentEvent.EventType getType();
  }
}
