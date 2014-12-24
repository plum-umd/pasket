package javax.swing.text;

public interface Document {
  public int getLength();
  public String getText(int offset, int length);
}
