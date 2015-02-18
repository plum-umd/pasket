package javax.swing.text;

public abstract class AbstractDocument implements Document {
  public void addDocumentListener(DocumentListener listener);
  public int getLength();
  public String getText(int offset, int length);

  public class DefaultDocumentEvent implements DocumentEvent {
    public DefaultDocumentEvent(int off, int len, String type);
    public Document getDocument();
  }
}
