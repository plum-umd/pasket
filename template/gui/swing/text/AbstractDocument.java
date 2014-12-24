package javax.swing.text;

public abstract class AbstractDocument implements Document {
  public int getLength();
  public String getText(int offset, int length);
}
