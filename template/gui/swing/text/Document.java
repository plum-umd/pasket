package javax.swing.text;

@ObserverPattern(DocumentEvent)
public interface Document {
  public void addDocumentListener(DocumentListener listener);
  public int getLength();
  public String getText(int offset, int length);
}
